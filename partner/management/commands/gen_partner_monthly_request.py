from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, CharField
from django.db.models.functions import Concat
from django.utils import timezone

from master.models import BatchManage
from contract.models import Contract
from partner.models import PartnerCompany, PartnerMember, PartnerMonthlyRequest
from utils import common, constants
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'gen_partner_monthly_request'
    BATCH_TITLE = '月別の協力社員請求情報作成'
    help = '''今月から六か月まで先の協力社員月別請求を作成
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--date',
            default=timezone.localtime().date(),
            help='請求作成対象日'
        )

    def handle(self, *args, **options):
        execute_date = self.get_date_argument('date', **options)
        execute_date = common.add_months(execute_date, constants.PARTNER_MEMBER_MONTHLY_REQUEST_FORWARD + 1)
        year = execute_date.strftime('%Y')
        month = execute_date.strftime('%m')
        company_content_type = ContentType.objects.get_for_model(PartnerCompany)
        member_content_type = ContentType.objects.get_for_model(PartnerMember)
        cnt = 0
        # 今月から七か月目　注文書またはBP請求書未作成の月別請求情報を削除する。
        PartnerMonthlyRequest.objects.annotate(
            start_ym=Concat('year', 'month', output_field=CharField()),
            end_ym=Concat('end_year', 'end_month', output_field=CharField()),
        ).filter(
            Q(year=year, month=month, end_year=None, end_month=None) |
            Q(start_ym__lte=year + month, end_ym__gte=year + month),
            is_submitted=False,
        ).delete()
        # 注文書またはBP請求書作成済の月別請求情報
        qs_monthly_request = PartnerMonthlyRequest.objects.filter(
            year=year,
            month=month,
        )
        # 今月から七か月目の月別請求情報を作成する。
        for contract in Contract.objects.filter(
            Q(company_content_type=company_content_type) | Q(company_content_type=member_content_type),
            is_deleted=False,
            start_date__lte=common.get_last_day_by_month(execute_date),
            end_date__gte=common.get_first_day_by_month(execute_date),
        ).exclude(
            partnermonthlyrequest__in=qs_monthly_request,
        ):
            PartnerMonthlyRequest.create_monthly_request(None, contract, year, month)
            self.logger.debug('{}の{}年{}月の請求情報を作成しました。'.format(
                contract.content_object,
                year,
                month,
            ))
            cnt += 1
        self.logger.info('{}年{}月に{}件データを処理しました。'.format(year, month, cnt))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
