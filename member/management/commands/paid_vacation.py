from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from master.models import BatchManage, Config, Company
from member.biz import get_member_join_date
from member.models import Member, PaidVacation
from utils import common
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'paid_vacation'
    BATCH_TITLE = '社員有休'
    help = """指定年月の社員有休日数を設定する。
計算対象は社員だけ、協力社員と個人事業主は対象外です。
下記のルールによって、有休日数を計算されています。
-------------------------------
勤続年数  6月   1年6月   2年6月   3年6月  4年6月   5年6月   6年6月   以降1年経過ごと
付与日数  10日  11日     12日     14日    16日     18日     20日     20日
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--date',
            default=timezone.localtime().date(),
            help='社員有休計算日',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        execute_date = self.get_date_argument('date', **options)
        first_day = common.get_first_day_by_month(execute_date)
        last_day = common.get_last_day_by_month(execute_date)
        reserve_month = Config.get_paid_vacation_forward_month()
        new_start_date = common.get_first_day_by_month(common.add_months(execute_date, reserve_month))
        ct_company = ContentType.objects.get_for_model(Company)
        ct_member = ContentType.objects.get_for_model(Member)
        # 契約中の社員
        qs_all_members = Member.objects.filter(
            is_deleted=False,
            contracts__is_deleted=False,
            contracts__status__lt='90',
            contracts__company_content_type=ct_company,
            contracts__content_type=ct_member,
            contracts__start_date__lte=last_day,
            contracts__end_date__gte=first_day,
        ).distinct()
        # 有休作成済の社員
        qs_existed = Member.objects.filter(
            is_deleted=False,
            paidvacation__end_date__gt=new_start_date,
        ).distinct()
        paid_vacation_period_list = Config.get_paid_vacation_intervals()
        # 有休上限月数（これ以上超えると有休日数は増えない）
        max_end_months = max([i[1] for i in paid_vacation_period_list])
        cnt = 0
        for member in qs_all_members.exclude(pk__in=qs_existed):
            join_date = get_member_join_date(member)
            # 入社月数
            months = common.get_interval_months(join_date, new_start_date)
            if months < max_end_months:
                period_list = [i for i in paid_vacation_period_list if i[0] <= months < i[1]]
                if len(period_list) == 0:
                    continue
                start_months, end_months, days = period_list[0]
            else:
                start_months, end_months, days = paid_vacation_period_list[-1]
                start_index = int((months - 6) / 12)
                start_months = start_index * 12 + 6
                end_months = start_months + 12
            start_date = common.get_first_day_by_month(common.add_months(join_date, start_months))
            end_date = common.get_last_day_by_month(common.add_months(join_date, end_months - 1))
            # 前年度の繰越日数を取得する
            carryover_days = PaidVacation.get_carryover_days(member, common.add_months(start_date, -1))
            PaidVacation.objects.create(
                member=member,
                start_date=start_date,
                end_date=end_date,
                days=days,
                carryover_days=carryover_days,
            )
            cnt += 1
        self.logger.info('{}件データを処理しました。'.format(cnt))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
