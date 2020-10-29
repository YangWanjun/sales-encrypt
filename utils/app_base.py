import os
import datetime
import requests
import random
import base64
import subprocess

from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags import humanize

from master.models import Config, Holiday
from org.models import Organization
from utils import constants, common, jpholiday
from utils.errors import CustomException

signer = TimestampSigner()


def get_tmp_path():
    """一時フォルダーを取得する。

    :return:
    """
    path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def get_media_root():
    return settings.MEDIA_ROOT


def get_template_path():
    path = os.path.join(settings.MEDIA_ROOT, 'template')
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def get_sub_tmp_path():
    """一時フォルダー配下にさらに一時フォルダーを取得する

    :return:
    """
    name = "{0}_{1}".format(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
        random.randint(10000, 99999),
    )
    tmp_path = os.path.join(get_tmp_path(), name)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    return tmp_path


def get_tmp_file(ext):
    """一時フォルダー配下にさらに一時ファイルを取得する

    :return:
    """
    name = "{0}_{1}.{2}".format(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
        random.randint(10000, 99999),
        ext,
    )
    tmp_path = os.path.join(get_tmp_path(), name)
    return tmp_path


def get_attendance_template_path():
    return os.path.join(get_template_path(), 'attendance_format.xlsx')


def get_worker_roster_template_path():
    return os.path.join(get_template_path(), 'worker_roster.xlsx')


def get_member_expense_template_path(is_row_over=False):
    """経費精算書テンプレートのパスを取得する

    :param is_row_over: 行数多い場合はもう一個のテンプレートを使用、このテンプレートは最多68件表示できます。
    :return:
    """
    if is_row_over:
        filename = 'expense_format_2.xlsx'
    else:
        filename = 'expense_format.xlsx'
    return os.path.join(get_template_path(), filename)


def convert_html_to_pdf(html):
    url = Config.get_convert_to_pdf_api()
    try:
        res = requests.post(url, {'content': html})
    except requests.exceptions.ConnectionError:
        raise CustomException(constants.ERROR_CANNOT_ESTABLISH_CONNECTION.format(name='PDFサーバー'))
    return res.status_code, res


def is_date_conflict(cls, pk, **kwargs):
    """期間が重複しているかどうか

    :param cls: 検索対象となるテーブルクラス
    :param pk: 変更の場合は主キー、追加の場合は None
    :param kwargs: 検索条件
    :return:
    """
    qs = cls.objects.filter(**kwargs)
    if pk:
        qs = qs.exclude(pk=pk)
    return qs.count() > 0


def check_conflict_objects(new_start_date, cls, pk, **kwargs):
    """時系列のデータを追加、変更時、新しい開始日は既存データの開始日以前より設定できないようにチェックする。

    :param new_start_date: 新しい開始日
    :param cls: 時系列のクラス
    :param pk: 変更の場合、主キー、追加の場合は空白
    :param kwargs:
    :return: True: 問題なし
    """
    qs = cls.objects.filter(**kwargs).filter(start_date__gte=new_start_date)
    if pk:
        qs = qs.exclude(pk=pk)
    if qs.count() >= 1:
        raise CustomException(constants.ERROR_DATE_CONFLICT_TO.format(
            date=new_start_date,
            object=qs.first()),
        )
    else:
        return True


def update_conflict_objects(qs, new_start_date):
    """時系列のデータに対して、データ追加または変更時、期間を重複しないように、直前データの期間を変更する。

    :param qs: 重複可能のデータセット
    :param new_start_date: 新しいデータの開始日
    :return:
    """
    if qs.count() > 1:
        date = qs.order_by('-start_date').first().start_date
        raise CustomException(constants.ERROR_DATE_CONFLICT.format(date=date))
    elif qs.count() == 1:
        obj = qs.first()
        if obj.start_date >= new_start_date:
            obj.is_deleted = True  # 論理削除
            obj.save(update_fields=('is_deleted', 'deleted_dt'))
        else:
            obj.end_date = common.add_days(new_start_date, -1)
            obj.save(update_fields=('end_date', 'updated_dt'))
        return obj
    else:
        return None


def restore_conflict_objects(qs):
    """時系列のデータに対して、データを削除時、直前のデータ期間を元に戻す。

    :param qs:
    :return:
    """
    if qs.count() > 1:
        date = qs.order_by('-start_date').first().start_date
        raise CustomException(constants.ERROR_DATE_CONFLICT.format(date=date))
    elif qs.count() == 1:
        for obj in qs:
            obj.end_date = obj.initial_end_date
            obj.save(update_fields=('end_date', 'updated_dt'))
            return obj
    else:
        return None


def get_expense_summary(dict_expenses):
    """請求書に出力する精算概要を取得する。

    :param dict_expenses: 分類名：　精算（Expenseのインスタンス）
    :return:
    """
    detail_expenses = []
    for key, value in dict_expenses.items():
        d = dict()
        member_list = []
        amount = 0
        for expense in value:
            member = expense.content_object
            member_list.append(member.last_name +
                               member.first_name +
                               "¥%s" % (expense.amount,))
            amount += expense.amount
        d['category_summary'] = "%s(%s)" % (key, "、".join(member_list))
        d['amount'] = amount
        detail_expenses.append(d)
    return detail_expenses


def check_file_size_limit(data):
    """ファイルサイズの制限チェック

    :param data: base64ファイルの文字列
    :return:
    """
    size = common.get_base64_file_size(data)  # 単位：バイト数
    limit = settings.FILE_UPLOAD_MAX_MEMORY_SIZE  # 単位：BYTE
    if size > limit:
        raise CustomException(constants.ERROR_FILE_SIZE_LIMIT.format(
            limit='{}MB'.format(int(limit / 1024 / 1024))
        ))
    else:
        return True


def log_action(user, instance, action_flg, message):
    """ログを記録する

    :param user: ログインユーザー
    :param instance: 変更対象のオブジェクト
    :param action_flg: 操作（追加／変更／削除）
    :param message: メッセージ
    :return:
    """
    LogEntry.objects.log_action(
        user.id,
        ContentType.objects.get_for_model(instance).pk,
        instance.pk,
        str(instance),
        action_flg,
        change_message=message
    )


def log_action_for_add(user, instance):
    log_action(user, instance, ADDITION, '[{"added": {}}]')


def log_action_for_delete(user, instance):
    log_action(user, instance, DELETION, '')


def log_action_for_change(user, instance, changed_data):
    """データ変更時のログを記録する

    :param user: ログインユーザー
    :param instance: 変更後のオブジェクト
    :param changed_data: 変更したデータリスト
    :return:
    """
    log_action(user, instance, CHANGE, '\n'.join(changed_data))


def get_org_code_from_request_data(data):
    """HTML請求から部署コードを取得する
    社員コードを取得するため

    :param data: HTML request data
    :return:
    """
    organization_info = data.get('organization')
    org_code = '00'
    if organization_info and 'organization' in organization_info:
        org = Organization.objects.get(pk=organization_info.get('organization'))
        division = org.get_root()
        if division:
            org_code = division.code
    return org_code


def create_monthly_request(content_object, contract, cls_monthly_request, qs_monthly_request, forward_months):
    """月別請求を作成する。

    :param content_object: 協力社員／案件メンバー
    :param contract: 契約
    :param cls_monthly_request: 月別請求クラス
    :param qs_monthly_request: 紐づきの月別請求
    :param forward_months: これから何っか月先の月別請求を作成する
    :return:
    """
    date = datetime.date.today()
    date = common.add_months(date, forward_months)
    last_day = common.get_last_day_by_month(date)
    tmp_date = contract.start_date
    while tmp_date <= last_day and tmp_date <= contract.end_date:
        year = tmp_date.strftime('%Y')
        month = tmp_date.strftime('%m')
        tmp_date = common.add_months(tmp_date, 1)
        qs = qs_monthly_request.filter(year=year, month=month, contract=contract)
        if qs.filter(is_submitted=True).count() > 0:
            continue
        qs.delete()
        cls_monthly_request.create_monthly_request(
            content_object, contract, year, month
        )
        if contract.is_blanket_contract:
            # 一括契約の場合月別請求は一件しかないのです。
            break


def get_base_amount_memo(amount, is_hourly_pay=False, is_fixed_pay=False):
    """基本給メモを取得する

    :param amount: 基本給
    :param is_hourly_pay: 時給
    :param is_fixed_pay: 固定金額
    :return:
    """
    if is_hourly_pay:
        str_format = Config.get_partner_order_base_amount_hourly()
    elif is_fixed_pay:
        str_format = Config.get_partner_order_base_amount_fixed()
    else:
        str_format = Config.get_partner_order_base_amount_common()
    return str_format.format(amount=humanize.intcomma(amount))


def get_hours_memo(min_hours, max_hours, is_hourly_pay, is_fixed_pay):
    if is_hourly_pay:
        return None
    elif is_fixed_pay:
        return None
    return Config.get_partner_order_hours_memo().format(min=min_hours, max=max_hours)


def get_minus_per_hour_memo(plus_per_hour, is_hourly_pay, is_fixed_pay):
    if is_hourly_pay:
        return None
    elif is_fixed_pay:
        return None
    else:
        return Config.get_partner_order_minus_per_hour().format(amount=humanize.intcomma(plus_per_hour))


def get_plus_per_hour_memo(minus_per_hour, is_hourly_pay, is_fixed_pay):
    if is_hourly_pay:
        return None
    elif is_fixed_pay:
        return None
    else:
        return Config.get_partner_order_plus_per_hour().format(amount=humanize.intcomma(minus_per_hour))


def get_company_square_signature_base64():
    """会社の角印を取得する。

    :return:
    """
    path = os.path.join(get_media_root(), 'stamp/square_signature.png')
    data = open(path, 'rb').read()
    return 'data:image/png;base64,%s' % (base64.b64encode(data).decode("ascii"),)


def get_user_fullname(user):
    """ログインユーザーの名称を取得する

    :param user:
    :return:
    """
    if hasattr(user, 'member'):
        return user.member.full_name
    elif user.first_name or user.last_name:
        return '{}{}{}'.format(user.last_name, ' ' if user.last_name and user.first_name else '', user.first_name)
    else:
        return user.username


def get_business_days(year, month):
    """営業日を取得

    :param year:
    :param month:
    :return:
    """
    dates = get_dates(year, month)
    return [item.get('date') for item in dates if item.get('is_holiday') is False]


def get_dates(year, month):
    """指定年月の日付リストを取得する。

    :param year: 対象年
    :param month: 対象月
    :return:
    """
    first_day = datetime.date(int(year), int(month), 1)
    last_day = common.get_last_day_by_month(first_day)
    lst_holiday = list(Holiday.objects.filter(
        is_deleted=False,
        date__lte=last_day,
        date__gte=first_day,
    ))
    dates = []
    tmp_date = first_day
    while tmp_date <= last_day:
        if tmp_date.weekday() in (5, 6):
            dates.append({
                'date': tmp_date,
                'is_holiday': True,
                'name': '休日',
            })
        elif jpholiday.is_holiday(tmp_date):
            dates.append({
                'date': tmp_date,
                'is_holiday': True,
                'name': jpholiday.get_holiday_name(tmp_date),
            })
        elif len([i for i in lst_holiday if i.date == tmp_date]) > 0:
            holiday = [i for i in lst_holiday if i.date == tmp_date][0]
            dates.append({
                'date': tmp_date,
                'is_holiday': True,
                'name': holiday.name,
            })
        else:
            dates.append({
                'date': tmp_date,
                'is_holiday': False,
                'name': None,
            })
        tmp_date += datetime.timedelta(days=1)
    return dates


def get_min_hours_by_month(calculate_type, year, month, default_hours):
    """指定年月の最低出勤時間を取得

    :param calculate_type:
    :param year:
    :param month:
    :param default_hours:
    :return:
    """
    count = len(get_business_days(year, month))
    if calculate_type == '01':
        # 固定１６０時間
        return 160
    elif calculate_type == '02':
        # 営業日数 × ８
        return count * 8
    elif calculate_type == '03':
        # 営業日数 × ７.９
        return count * 7.9
    elif calculate_type == '04':
        # 営業日数 × ７.７５
        return count * 7.75
    else:
        # その他（任意）
        return default_hours


def get_payment_notice_deadline(year, month):
    """支払通知書とＢＰ請求書をメール送信時の支払締切日を取得する

    来月の第六営業日

    :param year: 対象年
    :param month: 対象月
    :return:
    """
    date = datetime.date(int(year), int(month), 1)
    next_month = common.add_months(date, 1)
    business_days = get_business_days(next_month.year, next_month.month)
    if len(business_days) > 5:
        return business_days[5]
    else:
        return next_month


def compress_multi_files(file_bytes, password=None):
    """複数のファイルを圧縮する

    :param file_bytes: (filename, bytes)のリスト
    :param password: パスワード
    :return:
    """
    tmp_files = []
    # tmpフォルダー配下の一時フォルダーを取得する
    tmp_path = get_sub_tmp_path()
    tmp_files.append(tmp_path)
    tmp_zip = get_tmp_file('zip')
    tmp_files.append(tmp_zip)
    for filename, tmp_file in file_bytes:
        new_path = os.path.join(tmp_path, filename)
        tmp_files.append(new_path)
        # バイナリーファイルを一時ファイルに書き込む
        with open(new_path, 'wb') as f:
            f.write(tmp_file)
    # tmpフォルダー配下すべてのファイル名をUTF8からShift-JISに変換する
    subprocess.call(["convmv", "-r", "-f", "utf8", '-t', 'cp932', '--notest', tmp_path.rstrip('/') + '/'])
    # 一時フォルダーを圧縮する
    if password:
        command = "zip --password {0} -j {1} {2}/*".format(password, tmp_zip, tmp_path.rstrip('/'))
    else:
        command = "zip -j {0} {1}/*".format(tmp_zip, tmp_path.rstrip('/'))
    subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bytes_data = open(tmp_zip, 'rb', ).read()
    return bytes_data


def get_signed_value(value):
    return signer.sign(value)


def get_unsigned_value(value):
    try:
        return signer.unsign(value, max_age=constants.DEFAULT_TIMEOUT)
    except SignatureExpired:
        return False
