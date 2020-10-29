from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from contract.models import Contract
from master.models import BatchManage
from project.models import ProjectMemberMonthlyRequest, ProjectMember
from utils import common, constants
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'gen_project_monthly_request'
    BATCH_TITLE = '月別の案件メンバー請求情報作成'

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--date',
            default=timezone.localtime().date(),
            help='請求作成対象日'
        )

    def handle(self, *args, **options):
        execute_date = self.get_date_argument('date', **options)
        execute_date = common.add_months(execute_date, constants.PROJECT_MEMBER_MONTHLY_REQUEST_FORWARD + 1)
        year = execute_date.strftime('%Y')
        month = execute_date.strftime('%m')
        ct_pm = ContentType.objects.get_for_model(ProjectMember)
        # 未使用の月別請求情報を削除してから再作成する。
        ProjectMemberMonthlyRequest.objects.filter(
            year=year,
            month=month,
            is_submitted=False,
        ).delete()
        cnt = 0
        for contract in Contract.objects.filter(
            is_deleted=False,
            content_type=ct_pm,
            start_date__lte=common.get_last_day_by_month(execute_date),
            end_date__gte=common.get_first_day_by_month(execute_date),
        ).exclude(
            projectmembermonthlyrequest__year=year,
            projectmembermonthlyrequest__month=month,
        ):
            project_member = contract.content_object
            ProjectMemberMonthlyRequest.create_monthly_request(project_member, contract, year, month)
            self.logger.debug('{}の{}年{}月の請求情報を作成しました。'.format(
                project_member,
                year,
                month,
            ))
            cnt += 1
        self.logger.info('{}件データを処理しました。'.format(cnt))

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
