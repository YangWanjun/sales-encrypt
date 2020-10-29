import re
import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import Max, ProtectedError
from django.utils import timezone

from utils import constants, common
from utils.errors import CustomException

logger = common.get_system_logger()


class DefaultManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super(DefaultManager, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def get_queryset(self):
        return super(DefaultManager, self).get_queryset().filter(*self.args, **self.kwargs)

    def public_all(self):
        return self.get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    created_dt = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    is_deleted = models.BooleanField(default=False, editable=False, verbose_name="削除フラグ")
    deleted_dt = models.DateTimeField(blank=True, null=True, editable=False, verbose_name="削除日時")

    objects = DefaultManager()

    class Meta:
        abstract = True

    # @transaction.atomic
    # def delete(self, using=None, keep_parents=False):
    #     self.is_deleted = True
    #     self.deleted_dt = timezone.now()
    #     self.save(update_fields=('is_deleted', 'deleted_dt'))


class BaseView(models.Model):
    objects = DefaultManager()

    class Meta:
        abstract = True
        default_permissions = ()


class AbstractCompany(BaseModel):
    code = models.CharField(max_length=4, blank=True, null=True, unique=True, verbose_name="会社コード")
    name = models.CharField(max_length=30, unique=True, verbose_name="会社名")
    kana = models.CharField(max_length=30, blank=True, null=True, verbose_name="フリカナ")
    president = models.CharField(max_length=30, blank=True, null=True, verbose_name="代表者名")
    found_date = models.DateField(blank=True, null=True, verbose_name="設立年月日")
    capital = models.BigIntegerField(blank=True, null=True, verbose_name="資本金")
    post_code = models.CharField(
        blank=True, null=True, max_length=7, verbose_name="郵便番号",
        validators=(RegexValidator(regex=constants.REG_POST_CODE),),
    )
    address1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="住所１")
    address2 = models.CharField(max_length=100, blank=True, null=True, verbose_name="住所２")
    tel = models.CharField(
        max_length=11, blank=True, null=True, verbose_name="電話番号",
        validators=(RegexValidator(regex=constants.REG_TEL),)
    )
    fax = models.CharField(
        max_length=11, blank=True, null=True, verbose_name="ファックス",
        validators=(RegexValidator(regex=constants.REG_FAX),)
    )
    payment_month = models.CharField(
        blank=True, null=True, max_length=1, default='1',
        choices=constants.CHOICE_PAYMENT_MONTH, verbose_name="支払いサイト"
    )
    payment_day = models.CharField(
        blank=True, null=True, max_length=2, choices=constants.CHOICE_PAYMENT_DAY,
        default='99', verbose_name="支払日"
    )
    decimal_type = models.CharField(
        max_length=1, default='0', choices=constants.CHOICE_DECIMAL_TYPE,
        verbose_name="小数の処理区分"
    )
    attendance_type = models.CharField(
        max_length=1, default='1', choices=constants.CHOICE_ATTENDANCE_TYPE, verbose_name="出勤の計算区分"
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def address(self):
        return '{}{}'.format(self.address1 or '', self.address2 or '')

    def get_pay_date(self, year=None, month=None):
        """支払い期限日を取得する。

        :param year: 対象年
        :param month: 対象月
        :return:
        """
        if year is None and month is None:
            date = datetime.date.today()
        else:
            date = datetime.date(int(year), int(month), 1)
        months = int(self.payment_month) if self.payment_month else 1
        pay_month = common.add_months(date, months)
        if self.payment_day == '99' or not self.payment_day:
            return common.get_last_day_by_month(pay_month)
        else:
            pay_day = int(self.payment_day)
            last_day = common.get_last_day_by_month(pay_month)
            if last_day.day < pay_day:
                return last_day
            return datetime.date(pay_month.year, pay_month.month, pay_day)


class AbstractMember(BaseModel):
    code = models.CharField(max_length=7, unique=True, verbose_name="コード")
    last_name = models.CharField(max_length=10, verbose_name="姓")
    first_name = models.CharField(max_length=10, verbose_name="名")
    last_name_ja = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="姓(フリカナ)"
    )
    first_name_ja = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="名(フリカナ)"
    )
    last_name_en = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="姓(ローマ字)",
        help_text="漢字ごとに先頭文字は大文字にしてください（例：XiaoWang）"
    )
    first_name_en = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="名(ローマ字)",
        help_text="先頭文字は大文字にしてください（例：Zhang）"
    )
    common_first_name = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="通称名（名）"
    )
    common_last_name = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="通称名（姓）"
    )
    common_first_name_ja = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="通称名（名）(カナ)"
    )
    common_last_name_ja = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="通称名（姓）(カナ)"
    )
    gender = models.CharField(
        max_length=1, blank=True, null=True, choices=constants.CHOICE_GENDER, verbose_name="性別"
    )
    country = models.CharField(
        max_length=3, blank=True, null=True, choices=constants.CHOICE_COUNTRY, verbose_name="国籍・地域"
    )
    birthday = models.DateField(blank=True, null=True, verbose_name="生年月日")
    graduate_date = models.DateField(blank=True, null=True, editable=False, verbose_name="卒業年月日")
    join_date = models.DateField(blank=True, null=True, verbose_name="入社年月日")
    japan_start_date = models.DateField(blank=True, null=True, verbose_name="来日年月日")
    it_start_date = models.DateField(blank=True, null=True, verbose_name="IT仕事開始年月日")
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name="会社メールアドレス")
    private_email = models.EmailField(blank=True, null=True, unique=True, verbose_name="個人メールアドレス")
    post_code = models.CharField(
        max_length=7, blank=True, null=True, verbose_name="郵便番号",
        validators=(RegexValidator(regex=constants.REG_POST_CODE),),
        help_text="数値だけを入力してください、例：1230034"
    )
    address1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="住所１")
    address2 = models.CharField(max_length=100, blank=True, null=True, verbose_name="住所２")
    nearest_station = models.CharField(max_length=50, blank=True, null=True, verbose_name="最寄駅")
    phone = models.CharField(
        max_length=11, blank=True, null=True, verbose_name="携帯番号",
        validators=(RegexValidator(regex=constants.REG_PHONE),),
        help_text="数値だけを入力してください、例：08012345678"
    )
    marriage = models.CharField(
        max_length=1, blank=True, null=True,
        choices=constants.CHOICE_MARRIED, verbose_name="婚姻状況"
    )
    passport_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="パスポート番号")
    passport_expired_date = models.DateField(blank=True, null=True, verbose_name="パスポート有効期限")
    passport_image = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="パスポートの写し")
    personal_number = models.CharField(max_length=12, blank=True, null=True, verbose_name="個人番号")
    personal_number_image = models.CharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name="個人番号の写し（表面）"
    )
    personal_number_image_back = models.CharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name="個人番号の写し（裏面）"
    )
    avatar = models.ImageField(blank=True, null=True, upload_to='avatar/', verbose_name="写真")
    is_on_sales = models.BooleanField(default=False, verbose_name="営業対象")
    salesperson_id = models.PositiveIntegerField(blank=True, null=True, editable=False, verbose_name="営業員ID")
    comment = models.CharField(max_length=250, blank=True, null=True, verbose_name="備考")

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return '{} {}'.format(self.last_name, self.first_name)

    @property
    def full_kana(self):
        return '{} {}'.format(self.last_name_ja or '', self.first_name_ja or '').strip()

    @property
    def address(self):
        return '{}{}'.format(self.address1 or '', self.address2 or '')

    @classmethod
    def get_next_member_code(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_next_code_by_prefix(cls, prefix, length=constants.DEFAULT_MEMBER_CODE_LENGTH):
        prefix_len = len(prefix)
        num_len = length - prefix_len
        member = cls.objects.filter(code__iregex=r'{}[0-9]+'.format(prefix)).order_by('-code').first()
        if member:
            # 社員コード中の番号を取得する、自動採番のため。
            m = common.search_str(member.code[prefix_len:], constants.REG_NUMBER_TAIL)
            num = int(m[0]) if m else 0
            return prefix + str(num + 1).zfill(num_len)
        else:
            return prefix + '1'.zfill(num_len)

    def get_related_content_by_ym(self, year, month, qs, name):
        """指定年月の所属部署または契約を取得

        :param year: 対象年
        :param month: 対象月
        :param qs: クエリセット
        :param name: 検索対象の名前
        :return:
        """
        date = datetime.date(int(year), int(month), 1)
        first_day = common.get_first_day_by_month(date)
        last_day = common.get_last_day_by_month(date)
        try:
            return qs.get(
                is_deleted=False,
                start_date__lte=last_day,
                end_date__gte=first_day,
            )
        except ObjectDoesNotExist:
            message = constants.ERROR_NO_CONTENT_IN_YM.format(
                name=self.full_name,
                year=year,
                month=month,
                content=name,
            )
            logger.warn(message)
            return None
        except MultipleObjectsReturned:
            message = constants.ERROR_MULTI_CONTENT_IN_YM.format(
                name=self.full_name,
                year=year,
                month=month,
                content=name,
            )
            logger.warn(message)
            return None

    def get_organization(self, year, month):
        raise NotImplementedError

    def get_contract(self, year, month):
        raise NotImplementedError

    def get_cascade_organizations(self, year, month):
        """所属の事業部、部、課を取得する

        :param year: 所属年
        :param month: 所属月
        :return:
        """
        organization = self.get_organization(year, month)
        if organization:
            return organization.get_cascade_organizations()
        else:
            return None, None, None

    def get_release_date(self):
        end_date = None
        for project_member in self.project_members.all():
            for c in project_member.contracts.all():
                if end_date is None:
                    end_date = c.end_date
                elif end_date < c.end_date:
                    end_date = c.end_date
        return end_date

    @transaction.atomic
    def retire(self, retired_date):
        """退職処理を行います。

        :param retired_date: 退職日
        :return:
        """
        qs_pm = self.project_members.filter(
            contracts__end_date__gt=retired_date,
        ).distinct()
        if qs_pm.count() > 0:
            raise CustomException(constants.ERROR_CANNOT_RETIRE_FOR_PROJECT.format(name=qs_pm.first().project.name))
        # 未開始の契約を論理削除
        self.contracts.filter(
            start_date__gt=retired_date
        ).update(
            is_deleted=True,
            deleted_dt=timezone.now(),
        )
        # 契約中の契約終了日を退職日に設定
        from member.models import Retirement
        for contract in self.contracts.filter(
            is_deleted=False,
            status__lt='90',
            start_date__lt=retired_date,
            end_date__gt=retired_date,
        ):
            contract.end_date = retired_date
            contract.save(update_fields=('end_date', 'updated_dt'))
            Retirement.objects.create(
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
                retire_date=retired_date,
                contract=contract,
            )
        # 所属部署の配属終了日を退職日に設定
        self.organizations.filter(
            start_date__gt=retired_date
        ).delete()
        self.organizations.filter(
            start_date__lt=retired_date,
            end_date__gt=retired_date,
        ).update(
            end_date=retired_date,
        )
        # 営業対象から外す
        self.is_on_sales = False
        self.save(update_fields=('is_on_sales', 'updated_dt'))

    @property
    def is_retired(self):
        today = datetime.date.today()
        return self.contracts.filter(
            is_deleted=False,
            end_date__gte=today,
        ).count() == 0

    def get_current_project_members(self):
        today = datetime.date.today()
        qs = self.project_members.filter(
            is_deleted=False,
            contracts__end_date__gte=today,
        ).distinct()
        return qs

    def get_org_superior(self):
        """社員所属部署の上司を取得する

        :return:
        """
        today = datetime.date.today()
        organization = self.get_organization(today.strftime('%Y'), today.strftime('%m'))
        return self.get_superior(organization)

    def get_superior(self, organization):
        if organization:
            chief = organization.get_chief()
            if (chief is None or chief.member == self) and organization.parent:
                # 所属部署の部門長は自分自身の場合、親部署の部門長を取得する
                return organization.parent.get_chief()
            else:
                return chief
        else:
            return None

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        # アサイン済みの場合は削除できません、先に案件メンバーを削除する必要があります。
        if self.project_members.count() > 0:
            raise ProtectedError(constants.ERROR_DELETE_PROTECTED, self.project_members.all())
        # 所属した部署も削除
        self.organizations.all().delete()
        # 重複の紐づきが存在する場合も削除
        self.duplications_from.all().delete()
        self.duplications_to.all().delete()
        # 銀行口座を削除
        self.bank_accounts.all().delete()
        # 扶養家族
        self.families.all().delete()
        # 緊急連絡先
        self.emergency_contacts.all().delete()
        # 在留資格
        self.residences.all().delete()
        # 添付ファイル
        self.attachments.all().delete()
        return super(AbstractMember, self).delete(using, keep_parents)


class AbstractBankAccount(BaseModel):
    branch_no = models.CharField(max_length=3, validators=(RegexValidator(regex=r'[0-9]{3}'),), verbose_name="支店番号")
    branch_name = models.CharField(max_length=20, verbose_name="支店名称")
    branch_kana = models.CharField(max_length=40, blank=True, null=True, verbose_name="支店カナ",)
    account_type = models.CharField(max_length=1, choices=constants.CHOICE_BANK_ACCOUNT_TYPE, verbose_name="預金種類")
    account_number = models.CharField(
        max_length=8, validators=(RegexValidator(regex=r'[0-9]{7}'),), verbose_name="口座番号"
    )
    account_holder = models.CharField(blank=True, null=True, max_length=30, verbose_name="口座名義")

    class Meta:
        abstract = True


class AbstractMonthlyRequest(BaseModel):
    # 対象年月
    year = models.CharField(max_length=4, validators=(RegexValidator(regex=r'^\d{4}$'),), verbose_name="対象年")
    month = models.CharField(max_length=2, validators=(RegexValidator(regex=r'^\d{2}$'),), verbose_name="対象月")
    end_year = models.CharField(max_length=4, blank=True, null=True, verbose_name="終了年")
    end_month = models.CharField(max_length=2, blank=True, null=True, verbose_name="終了月")
    # 請求情報
    price = models.IntegerField(default=0, verbose_name="単価（税抜）")
    min_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="基準時間")
    max_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="最大時間")
    minus_per_hour = models.IntegerField(default=0, verbose_name="減（円）")
    plus_per_hour = models.IntegerField(default=0, verbose_name="増（円）")
    is_blanket_contract = models.BooleanField(default=False, verbose_name="一括案件")
    is_fixed_pay = models.BooleanField(default=False, verbose_name="固定金額")
    is_hourly_pay = models.BooleanField(
        default=False, verbose_name="時給",
        help_text='時給が設定したら、単価などの精算条件が無視される'
    )
    hourly_pay_amount = models.IntegerField(
        default=0, verbose_name="時給（税抜）",
        help_text='時給が設定したら、単価などの精算条件が無視される'
    )
    amount_other = models.PositiveIntegerField(default=0, verbose_name="その他の金額")
    amount_other_memo = models.CharField(max_length=200, blank=True, null=True, verbose_name="その他の金額メモ")
    is_submitted = models.BooleanField(default=False, verbose_name="この精算条件でファイルを作成済なのか")

    class Meta:
        abstract = True


class AbstractRequest(BaseModel):
    year = models.CharField(max_length=4, validators=(RegexValidator(regex=r'^\d{4}$'),), verbose_name="請求年")
    month = models.CharField(max_length=2, validators=(RegexValidator(regex=r'^\d{2}$'),), verbose_name="請求月")
    request_no = models.CharField(max_length=7, unique=True, verbose_name="請求番号")
    request_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="請求名称")
    amount = models.PositiveIntegerField(default=0, verbose_name="請求金額（税込）")
    tax_amount = models.PositiveIntegerField(default=0, verbose_name="税金")
    turnover_amount = models.IntegerField(default=0, verbose_name="売上金額(基本単価＋残業料)(税抜)")
    expense_amount = models.IntegerField(default=0, verbose_name="精算金額")

    class Meta:
        abstract = True

    @classmethod
    def get_next_request_no(cls, year, month):
        max_request_no = cls.objects.filter(year=year, month=month).aggregate(Max('request_no'))
        request_no = max_request_no.get('request_no__max')
        if request_no and re.match(constants.REG_REQUEST_NO, request_no):
            no = request_no[4:7]
            no = "%03d" % (int(no) + 1,)
            next_request_no = "%s%s%s" % (year[2:], month, no)
        else:
            next_request_no = "%s%s%s" % (year[2:], month, "001")
        return next_request_no


class AbstractRequestHeader(BaseModel):
    request_no = models.CharField(max_length=7, unique=True, verbose_name="請求番号")
    # 請求に関する情報
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    work_start_date = models.DateField(verbose_name="作業開始日")
    work_end_date = models.DateField(verbose_name="作業終了日")
    limit_date = models.DateField(verbose_name="お支払い期限")
    publish_date = models.DateField(verbose_name="発行日（対象月の最終日）")
    # 請求元会社情報
    company_name = models.CharField(max_length=30, verbose_name="会社名")
    company_master = models.CharField(max_length=30, blank=True, null=True, verbose_name="代表者名")
    company_post_code1 = models.CharField(max_length=3, blank=True, null=True, verbose_name="郵便番号")
    company_post_code2 = models.CharField(max_length=4, blank=True, null=True, verbose_name="郵便番号")
    company_address1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="住所１")
    company_address2 = models.CharField(max_length=100, blank=True, null=True, verbose_name="住所２")
    company_tel = models.CharField(max_length=11, blank=True, null=True, verbose_name="電話番号")
    company_fax = models.CharField(max_length=11, blank=True, null=True, verbose_name="ファックス")
    company_bank_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="金融機関名称")
    company_branch_no = models.CharField(max_length=3, blank=True, null=True, verbose_name="支店番号")
    company_branch_name = models.CharField(max_length=20, blank=True, null=True, verbose_name="支店名称")
    company_account_type = models.CharField(max_length=10, blank=True, null=True, verbose_name="預金種類")
    company_account_number = models.CharField(max_length=7, blank=True, null=True, verbose_name="口座番号")
    company_account_holder = models.CharField(max_length=30, blank=True, null=True, verbose_name="口座名義")
    # 請求先会社情報
    client_name = models.CharField(max_length=30, verbose_name="お客様名称")
    client_post_code1 = models.CharField(max_length=3, blank=True, null=True, verbose_name="お客様郵便番号")
    client_post_code2 = models.CharField(max_length=4, blank=True, null=True, verbose_name="お客様郵便番号")
    client_address1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="お客様住所１")
    client_address2 = models.CharField(max_length=100, blank=True, null=True, verbose_name="お客様住所２")
    client_tel = models.CharField(max_length=11, blank=True, null=True, verbose_name="お客様電話番号")
    client_fax = models.CharField(max_length=11, blank=True, null=True, verbose_name="お客様ファックス")

    class Meta:
        abstract = True


class AbstractRequestExpense(BaseModel):
    request_no = models.CharField(max_length=7, verbose_name="請求番号")
    category_summary = models.CharField(
        max_length=255, verbose_name="分類概要",
        help_text="指定分類の精算概要（例：交通費(○○1￥1200、○○2￥5000)）"
    )
    amount = models.PositiveIntegerField(verbose_name="精算金額")

    class Meta:
        abstract = True


class AbstractRequestDetail(BaseModel):
    request_no = models.CharField(max_length=7, verbose_name="請求番号")
    # 基本情報
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    is_blanket_contract = models.BooleanField(verbose_name="一括")
    is_hourly_pay = models.BooleanField(verbose_name="時給")
    member_type = models.CharField(
        max_length=2, blank=True, null=True, choices=constants.CHOICE_SIMPLE_MEMBER_TYPE, verbose_name="社員区分"
    )
    # 詳細情報
    item_no = models.PositiveSmallIntegerField(verbose_name="番号")
    item_name = models.CharField(max_length=50, verbose_name="項目名称")
    item_rate = models.DecimalField(max_digits=2, decimal_places=1, verbose_name="率")
    item_basic_amount = models.IntegerField(verbose_name="単価")
    item_min_max = models.CharField(max_length=20, blank=True, null=True, verbose_name="Min/Max（H）")
    item_min_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="基準時間")
    item_max_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="最大時間")
    item_minus_per_hour = models.IntegerField(verbose_name="減（円）")
    item_plus_per_hour = models.IntegerField(verbose_name="増（円）")
    item_total_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="合計時間")
    item_extra_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="残業時間")
    item_amount = models.IntegerField(default=0, verbose_name="請求金額（税込）")
    item_tax_amount = models.IntegerField(default=0, verbose_name="税金")
    item_turnover_amount = models.IntegerField(default=0, verbose_name="基本金額＋残業金額（税抜）")
    item_expense_amount = models.IntegerField(default=0, verbose_name="精算金額")
    item_comment = models.CharField(max_length=200, blank=True, null=True, verbose_name="備考")

    class Meta:
        abstract = True

    @property
    def item_minus_amount(self):
        """控除金額

        :return:
        """
        if self.item_extra_hours < 0:
            return abs(int(self.item_extra_hours * self.item_minus_per_hour))
        else:
            return 0

    @property
    def item_plus_amount(self):
        """超過金額

        :return:
        """
        if self.item_extra_hours > 0:
            return int(self.item_extra_hours * self.item_plus_per_hour)
        else:
            return 0
