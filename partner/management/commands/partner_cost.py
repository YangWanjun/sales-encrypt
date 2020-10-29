from django.db import transaction
from django.db.models import CharField
from django.db.models.functions import Concat
from django.utils import timezone

from master.models import BatchManage
from partner.models import PartnerOrder
from turnover.biz import add_partner_cost
from turnover.models import MonthlyCost
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'partner_cost'
    BATCH_TITLE = '協力会社コスト'

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--date',
            default=timezone.localtime().date(),
            help='コスト計算対象日',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        execute_date = self.get_date_argument('date', **options)
        year = execute_date.strftime('%Y')
        month = execute_date.strftime('%m')
        # 指定月に作成済のコスト情報を削除
        # 協力社員以外の社員と個人事業主のpartner_companyは全部空白
        qs_existed = MonthlyCost.objects.filter(partner_company__isnull=False, year=year, month=month)
        delete_cnt, dict_cnt = qs_existed.delete()
        self.logger.info('{year}年{month}月　{count}件の協力社員コスト情報が削除しました。'.format(
            year=year, month=month, count=delete_cnt,
        ))
        qs_order = PartnerOrder.objects.annotate(
                start_ym=Concat('year', 'month', output_field=CharField()),
                end_ym=Concat('end_year', 'end_month', output_field=CharField()),
        ).filter(
                is_deleted=False,
                start_ym__lte=year + month,
                end_ym__gte=year + month,
                member__isnull=False,
                company__isnull=False,
        )
        cnt_add = 0
        for order in qs_order:
            for partner_request_detail in order.partnerrequestdetail_set.filter(
                    is_deleted=False, year=year, month=month
            ):
                project_member = partner_request_detail.project_member
                add_partner_cost(
                    order.company,
                    project_member.member_content_object,
                    year,
                    month,
                    project_member.project,
                    partner_request_detail
                )
                cnt_add += 1
        self.logger.info('{year}年{month}月　{count}件の協力社員コスト情報が追加しました。'.format(
            year=year, month=month, count=cnt_add,
        ))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
