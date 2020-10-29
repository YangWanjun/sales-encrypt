import datetime

from master.models import BatchManage
from member.biz import set_member_status
from member.models import Member
from partner.models import PartnerMember
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'working_status'
    BATCH_TITLE = '稼働状態'

    def handle(self, *args, **options):
        today = datetime.date.today()
        year = today.strftime('%Y')
        month = today.strftime('%m')
        # 現在契約のある社員
        member_list = list(Member.objects.public_all().filter(
            contracts__start_date__lte=today,
            contracts__end_date__gte=today,
        ).distinct())
        partner_member_list = list(PartnerMember.objects.public_all().filter(
            contracts__start_date__lte=today,
            contracts__end_date__gte=today,
        ).distinct())
        member_count = 0
        waiting_count = 0
        working_count = 0
        for member in member_list + partner_member_list:
            member_count += 1
            info = set_member_status(member, year, month)
            if info.get('is_working'):
                working_count += 1
            else:
                waiting_count += 1

        self.logger.info('社員数：{member_count}／稼働数：{working_count}／待機数：{waiting_count}'.format(
            member_count=member_count,
            working_count=working_count,
            waiting_count=waiting_count,
        ))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
