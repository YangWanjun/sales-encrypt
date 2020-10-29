import datetime

from django.core.exceptions import ObjectDoesNotExist

from master.models import BatchManage, FirebaseTopic
from member.models import Member
from utils import constants
from utils.django_base import BaseBatch
from utils.firebase import send_message_to_topic


class Command(BaseBatch):
    BATCH_NAME = 'birthday'
    BATCH_TITLE = '誕生日通知'

    def handle(self, *args, **options):
        today = datetime.date.today()
        cnt = 0
        try:
            topic = FirebaseTopic.objects.get(name=self.BATCH_NAME)
        except ObjectDoesNotExist:
            self.logger.error(constants.ERROR_NO_TOPIC.format(topic=self.BATCH_NAME, process=self.BATCH_TITLE))
            return
        qs = Member.objects.filter(
            is_deleted=False,
            birthday__month=today.month,
            birthday__day=today.day,
            contracts__end_date__gte=today,  # 退職済は除外
        ).distinct()
        for member in qs:
            send_message_to_topic(
                topic,
                title='おめでとうございます！',
                body='{date}は {name} の誕生日です。'.format(date=today.strftime('%m月%d日'), name=member.full_name)
            )
            cnt += 1
        self.logger.info('{}件データを処理しました。'.format(cnt))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
