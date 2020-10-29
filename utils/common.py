import re
import datetime
import calendar
import logging
import math
import os
import uuid
import base64
import string
import random
import jaconv

from . import constants


def add_days(source_date, days=1):
    return source_date + datetime.timedelta(days=days)


def add_months(source_date, months=1):
    month = source_date.month - 1 + months
    year = int(source_date.year + month / 12)
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def get_first_day_by_month(source_date):
    return datetime.date(source_date.year, source_date.month, 1)


def get_last_day_by_month(source_date):
    next_month = add_months(source_date, 1)
    return next_month + datetime.timedelta(days=-next_month.day)


def get_interval_months(start_date, end_date):
    return (end_date.year * 12 + end_date.month) - (start_date.year * 12 + start_date.month)


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict

    :param cursor:
    :return:
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_ext_from_content_type(content_type):
    try:
        category, ext = content_type.split('/')
        return '.' + ext
    except ValueError:
        return None


def get_system_logger():
    """システムのロガーを取得する。

    :return:
    """
    return logging.getLogger('system')


def get_batch_logger(name):
    """バッチのロガーを取得する。

    :param name: バッチ名（ＩＤ）
    :return:
    """
    return logging.getLogger('batch.%s' % name)


def get_consumption_tax(amount, tax_rate, decimal_type):
    """消費税を取得する。

    :param amount:
    :param tax_rate:
    :param decimal_type:
    :return:
    """
    if not amount:
        return 0
    return get_integer(decimal_type, float(amount) * float(tax_rate))


def get_integer(decimal_type, value):
    """整数を取得する

    :param decimal_type: 小数の処理区分
    :param value:
    :return:
    """
    if decimal_type == '0':
        # 四捨五入
        return round(value)
    elif decimal_type == '1':
        # 切り捨て
        return math.floor(value)
    elif decimal_type == '2':
        # 切り上げ
        return math.ceil(value)
    else:
        # 四捨五入
        raise round(value)


def get_real_attendance_hours(attendance_type, hours):
    """実際の出勤時間を取得

    :param attendance_type: 出勤の計算区分
    :param hours: 出勤時間
    :return:
    """
    decimal_part, integer_part = math.modf(hours)
    if decimal_part == 0:
        return integer_part
    elif attendance_type == '1':
        # １５分ごと
        if decimal_part < 0.25:
            return integer_part
        elif 0.25 <= decimal_part < 0.5:
            return integer_part + 0.25
        elif 0.5 <= decimal_part < 0.75:
            return integer_part + 0.5
        else:
            return integer_part + 0.75
    elif attendance_type == '2':
        # ３０分ごと
        if decimal_part < 0.5:
            return integer_part
        else:
            return integer_part + 0.5
    elif attendance_type == '4':
        # 六分ごと
        return math.floor(hours * 10) / 10
    else:
        # １時間ごと
        return integer_part


def get_minus_per_hour(decimal_type, price, min_hours):
    """控除時給を取得

    :param decimal_type: 小数の処理区分
    :param price: 単価
    :param min_hours: 最小時間
    :return:
    """
    if min_hours:
        return get_integer(decimal_type, price / min_hours)
    else:
        return 0


def get_plus_per_hour(decimal_type, price, max_hours):
    """残業時給を取得

    :param decimal_type: 小数の処理区分
    :param price: 単価
    :param max_hours: 最大時間
    :return:
    """
    if max_hours:
        return get_integer(decimal_type, price / max_hours)
    else:
        return 0


def search_str(s, pattern):
    """対象文字列から、特定の文字を取得する

    :param s: 検索対象文字列
    :param pattern: 正規表現
    :return:
    """
    m = re.search(pattern, s)
    return m.groups() if m else None


def get_attachment_path(self, filename):
    name, ext = os.path.splitext(filename)
    now = datetime.datetime.now()
    path = os.path.join(now.strftime('%Y'), now.strftime('%m'))
    return os.path.join(path, self.uuid + ext)


def is_base64_string(data):
    if isinstance(data, str):
        return re.search(r';base64,', data) is not None
    else:
        return False


def split_base64(base64_data):
    """Base64ファイルを解析する
    現在システムにカスタマイズしたbase64ファイル形式は下記通りです。
    name:xxxxxxxxxx=;data:image/jepg;base64,/9j/AAAAAAAAAAAA

    :param base64_data: カスタマイズしたbase64文字列
    :return:
    """
    return base64_data.split(';base64,')


def get_base64_file_size(base64_data):
    """Base64ファイルのサイズを取得する。

    :param base64_data: カスタマイズしたbase64文字列
    :return: バイト数を返す
    """
    if is_base64_string(base64_data):
        name_and_ext, data = split_base64(base64_data)
        return len(data) * 3 / 4 - data.count('=', -2)
    else:
        return 0


def get_ext_from_base64(base64_data):
    m = search_str(base64_data, constants.REG_BASE64_MIME_TYPE)
    mime_type = m[1] if m else None
    if mime_type == 'x-zip-compressed':
        return '.zip'
    elif mime_type is None:
        return ''
    elif mime_type.find('ms-excel') >= 0:
        return '.xlsx'
    else:
        return '.' + mime_type


def get_name_from_base64(base64_data):
    m = search_str(base64_data, constants.REG_BASE64_FILENAME)
    if m:
        return base64.b64decode(m[0]).decode('utf-8')
    else:
        return None


def get_default_file_uuid():
    return '{date}_{uuid}'.format(
        date=datetime.datetime.now().strftime('%y%m%d'),
        uuid=uuid.uuid4(),
    )


def escape_filename(filename):
    if filename:
        return re.sub(r'[<>:"/\\|?*]', '', filename)
    else:
        return filename


def get_request_filename(request_no, request_name, ext='.pdf'):
    """生成された請求書のパスを取得する。

    :param request_no: 請求番号
    :param request_name: 請求名称
    :param ext: 拡張子
    :return:
    """
    filename = "請求書_{request_no}_{name}".format(
        request_no=request_no,
        name=escape_filename(request_name),
    )
    return filename + ext


def get_payment_notice_filename(payment_notice_no, payment_notice_name, ext='.pdf'):
    filename = "支払通知書_{payment_notice_no}_{name}".format(
        payment_notice_no=payment_notice_no,
        name=escape_filename(payment_notice_name),
    )
    return filename + ext


def get_partner_order_filename(order_no, name, ext='.pdf'):
    """生成されたBP註文書のパスを取得する。

    :param order_no: 請求番号
    :param name: 名前（社員名・案件名）
    :param ext: 拡張子
    :return:
    """
    filename = "注文書_{order_no}_{name}".format(
        order_no=order_no,
        name=escape_filename(name),
    )
    return filename + ext


def get_partner_order_request_filename(order_no, name, ext='.pdf'):
    """生成されたBP註文請書のパスを取得する。

    :param order_no: 請求番号
    :param name: 名前（社員名・案件名）
    :param ext: 拡張子
    :return:
    """
    filename = "注文請書_{order_no}_{name}".format(
        order_no=order_no,
        name=escape_filename(name),
    )
    return filename + ext


def get_name_from_choice(value, choice):
    """選択肢から値によって、表示名称を取得する

    :param value: 値
    :param choice: 選択肢
    :return:
    """
    for k, v in choice:
        if k == value:
            return v
    return None


def join_html(html1, html2):
    """二つのＨＴＭＬを１つに結合する

    :param html1:
    :param html2:
    :return:
    """
    # 二つ目のHTML中で、<body></body>中身の内容を取り出す。
    pattern = re.compile('<body[^<>]*>(.+)</body>', re.MULTILINE | re.DOTALL)
    m = pattern.search(html2)
    if m:
        html2 = m.groups()[0]
    end_body_index = html1.rfind('</body>')
    if end_body_index > 0:
        return html1[:end_body_index] + html2 + '</body></html>'
    else:
        return html1 + html2


def generate_password(length=8):
    """パスワードを作成
    英文字と数字の組み合わせ

    :param length: パスワードの桁数
    :return:
    """
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def to_full_size(s, ignore='', kana=True, digit=True, ascii=True):
    if not s:
        return s
    return jaconv.h2z(s, ignore=ignore, kana=kana, digit=digit, ascii=ascii)


def to_half_size(s, ignore='', kana=True, digit=True, ascii=True):
    if not s:
        return s
    return jaconv.z2h(s, ignore=ignore, kana=kana, digit=digit, ascii=ascii)


def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
