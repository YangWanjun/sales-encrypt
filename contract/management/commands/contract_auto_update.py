from django.db import transaction
from django.utils import timezone

from contract.models import Contract
from master.models import BatchManage
from utils import common, constants
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'contract_auto_update'
    BATCH_TITLE = '契約自動更新'

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.now().date()
        next_month = common.add_months(today, 1)
        qs = Contract.objects.public_all().filter(
            contract_type__in=['0010', '0011', '0012'],  # 契約社員、パート、アルバイト
            status__lt='90',  # 破棄してない
            is_auto_update=True,  # 自動更新
            end_date__gte=today,
            end_date__lte=next_month,  # 一か月前に更新する
            children__isnull=True,
        ).distinct()
        for contract in qs:
            list_contract_comment = list(contract.contractcomment_set.filter(is_deleted=False))
            list_contract_calculate_hours = list(contract.contractcalculatehours_set.filter(is_deleted=False))
            list_contract_allowance = list(contract.contractallowance_set.filter(is_deleted=False))
            parent_id = contract.pk
            auto_update_period = contract.auto_update_period or 12
            contract.pk = None
            contract.contract_date = today
            contract.contract_no = Contract.get_next_contract_no(
                content_type=contract.content_type,
                object_id=contract.object_id,
                company_code=contract.company_content_object.code,
                object_code=contract.content_object.code,
            )
            contract.start_date = common.add_days(contract.end_date)
            contract.end_date = common.add_months(contract.end_date, contract.auto_update_period or 12)
            contract.parent_id = parent_id
            contract.auto_update_period = auto_update_period
            contract.status = '10'  # 自動更新済
            contract.save()
            # 契約項目
            for item in list_contract_comment:
                item.pk = None
                item.contract = contract
                item.save()
            # 契約計算用時間
            for item in list_contract_calculate_hours:
                item.pk = None
                item.contract = contract
                item.save()
            # 契約手当
            for item in list_contract_allowance:
                item.pk = None
                item.contract = contract
                item.save()
            self.logger.info(constants.INFO_CONTRACT_AUTO_UPDATED.format(
                name=contract.content_object,
                start_date=contract.start_date,
                end_date=contract.end_date,
            ))
        self.logger.info(constants.INFO_CONTRACT_UPDATED_COUNT.format(count=qs.count()))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
