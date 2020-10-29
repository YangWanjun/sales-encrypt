import datetime
from django.urls import reverse
from rest_framework import status as rest_status
from contract.models import Contract
from member.models import MemberWorkingStatus
from utils import common
from utils.test_base import BaseAPITestCase


# Create your tests here.
class MemberTest(BaseAPITestCase):

    def test_add_member_contract(self):
        self.client.login(username='admin', password='admin')
        url = reverse('contract-add-contract')
        today = datetime.date.today()
        start_date = common.get_first_day_by_month(common.add_months(today, -1))
        end_date = common.get_last_day_by_month(common.add_months(today, 6))
        response = self.client.post(url, data={
            "company_content_type": 11,  # 自社
            "company_object_id": 1,
            "content_type": 29,  # 社員
            "object_id": 11,  # 正社員 契約なし０１
            "contract_date": today,
            "contract_type": "0001",  # 正社員
            "start_date": start_date,
            "end_date": end_date,
            "contract_items": [
                {"code": "0001", "name": "雇用期間",
                 "content": "（期間満了の１ヶ月前までに、双方にいずれから書面による契約終了の申し出がないときは、同じ条件でさらに1年間更新されるものとし、その後も同様とする。）"},
                {"code": "0002", "name": "職位", "content": "一般社員"},
                {"code": "0003", "name": "就業の場所", "content": "就業の場所（当社社内および雇用者が指定した場所）"},
                {"code": "0004", "name": "業務の種類", "content": "業務の種類（一般社員）"},
                {"code": "0006", "name": "業務のコメント",
                 "content": "就業の場所および業務の種類は、業務の都合により変更することがある。\n出向、転勤、配置転換等の業務命令が発令されることがある。"},
                {"code": "0007", "name": "就業時間",
                 "content": "始業および終業時刻　午前　9時00分　～　午後　6時00分（1ケ月変形労働時間制による）\n"
                            "休憩時間　　　　　　　正午～午後1時\n"
                            "就業時間の変更　　前記にかかわらず業務の都合または就業場所変更により\n"
                            "　　　　　　　　　　　　　始業および終業時刻の変更を行うことがある。\n"
                            "所定労働時間を越える労働の有無　有"},
                {"code": "0200", "name": "給与締め切り日及び支払日", "content": "締切日及び支払日：毎月、月末日締め・翌月２５日払\n支払い方法：銀行振込"},
                {"code": "0201", "name": "昇給及び降給", "content": "会社の業績および社員個人の業績その他の状況を勘案し、昇給または降給を行うことがある。"},
                {"code": "0300", "name": "休日", "content": "週休2日制（土・日・祝祭日休み）"},
                {"code": "0301", "name": "有給休暇", "content": "年次有給休暇：労働基準法の定めによる。"},
                {"code": "0302", "name": "無給休暇", "content": "産前産後、育児・介護休業、生理休暇、その他就業規則に定めがあるときは当該休暇。"},
                {"code": "0800", "name": "退職に関する項目",
                 "content": "自己都合退職の場合　退職する１ヶ月前に届け出ること。\n解雇する場合　原則として　３０日前に予告すること。"},
                {"code": "9900", "name": "その他備考", "content": "1、個別合意又は就業規則の変更により、労働条件及び業務の変更等を行う場合がある\n"
                                                             "2、服務及び就業に関しては、前記並びに裏面、就業規則、諸規定、労働基準法その他関係法令の定めるところによる。"},
            ],
            "allowances": [
                {"code": "0001", "name": "基本給（税抜）", "amount": 600000, "unit": "01"},
            ],
        })
        # print(response.json())
        self.assertEqual(response.status_code, rest_status.HTTP_201_CREATED)
        if response.status_code == rest_status.HTTP_201_CREATED:
            contract = Contract.objects.get(pk=response.data["id"])
            self.assertEqual(contract.is_auto_update, False)
            self.assertEqual(contract.initial_end_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            # 稼働状態ワークテーブルに先月、今月と来月3件のレコードが作成されたこと。
            qs = MemberWorkingStatus.objects.filter(
                content_type_id=29,
                object_id=11,
            )
            self.assertEqual(qs.count(), 4)
            tmp_date = start_date
            while tmp_date < min(common.add_months(today, 3), end_date):
                qs = MemberWorkingStatus.objects.filter(
                    content_type_id=29,
                    object_id=11,
                    year=start_date.strftime('%Y'),
                    month=start_date.strftime('%m'),
                )
                self.assertEqual(qs.count(), 1)
                item = qs.first()
                self.assertEqual(item.release_date, None)
                self.assertEqual(item.salesperson_id, None)
                self.assertEqual(item.is_working, False)
                self.assertEqual(item.project, None)
                self.assertEqual(item.division_id, 10)
                self.assertEqual(item.department_id, 11)
                self.assertEqual(item.section_id, None)
                self.assertEqual(item.contract_id, contract.pk)
                tmp_date = common.add_months(tmp_date, 1)

