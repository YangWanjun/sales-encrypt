from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from attendance.models import Attendance
from attendance.biz import get_combined_attendance
from member.biz import get_project_members
from member.models import Member
from master.models import BatchManage, Company
from turnover.biz import add_employee_cost
from utils import common, constants
from utils.django_base import BaseBatch


class Command(BaseBatch):
    BATCH_NAME = 'employee_cost'
    BATCH_TITLE = '社員コスト'

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
        first_day = common.get_first_day_by_month(execute_date)
        last_day = common.get_last_day_by_month(execute_date)
        ct_company = ContentType.objects.get_for_model(Company)
        ct_member = ContentType.objects.get_for_model(Member)
        # 指定月に契約のある社員を洗い出す
        qs = Member.objects.filter(
            is_deleted=False,
            contracts__is_deleted=False,
            contracts__status__lt='90',
            contracts__company_content_type=ct_company,
            contracts__content_type=ct_member,
            contracts__start_date__lte=last_day,
            contracts__end_date__gte=first_day,
        ).distinct()
        # MonthlyCost.objects.filter(
        #     company_content_type=ct_company,
        #     member_content_type=ct_member,
        #     year=year,
        #     month=month,
        # ).delete()
        for member in qs:
            qs_attendance = Attendance.objects.filter(
                is_deleted=False,
                year=year,
                month=month,
                content_type=ct_member,
                object_id=member.pk,
            )
            project_members = get_project_members(member, year, month)
            if qs_attendance.count() == 0:
                attendance = None
            elif qs_attendance.count() == 1:
                attendance = qs_attendance.first()
            else:
                # 複数の案件に同時アサインした場合、複数出勤情報を合計する
                attendance = get_combined_attendance(qs_attendance)
            if project_members.count() > 0 and attendance is None:
                self.logger.warn(constants.ERROR_REQUIRE_ATTENDANCE.format(
                    name=member.full_name, year=year, month=month
                ))
            elif project_members.count() > 0:
                for project_member in project_members:
                    add_employee_cost(member, year, month, attendance, project_member.project)
            else:
                add_employee_cost(member, year, month, attendance, None)

    def get_batch_manager(self):
        """指定名称のバッチを取得する。

        :return:
        """
        return BatchManage.get_batch_by_name(self.BATCH_NAME)
