from django.urls import reverse
from utils.test_base import BaseAPITestCase


# Create your tests here.
class MemberTest(BaseAPITestCase):

    def test_add_member(self):
        self.client.login(username='admin', password='admin')
        url = reverse('member-add-from-contract')
        response = self.client.post(url, data={
            "basic_info": {
                "project": 1,  # add_projectで追加済の案件
                "member_content_type": 29,  # member.Member
                "member_object_id": 10,  # 正社員 契約あり０１
                "work_role": "SP"
            },
            "organization": {
                "contract_date": "2020-04-02",
                "calculate_hours": [
                    {"code": "0000", "name": "下限時間", "hours": 160},
                    {"code": "0001", "name": "上限時間", "hours": "200"},
                    {"code": "0010", "name": "計算用下限時間", "hours": 0},
                    {"code": "0011", "name": "計算用上限時間", "hours": 0}
                ],
                "allowances": [
                    {"code": "0001", "name": "基本給（税抜）", "unit": "01", "comment": "", "amount": 800000},
                    {"code": "1007", "name": "欠勤控除", "amount": 0, "unit": "03", "comment": ""},
                    {"code": "1008", "name": "残業手当", "amount": 0, "unit": "03", "comment": ""},
                    {"code": "9900", "name": "その他手当", "amount": 0, "unit": "01", "comment": ""}
                ],
                "contract_items": [
                    {"code": "9900", "name": "その他備考", "content": "固定50000円の交通費含む"}
                ],
                "contract_type": "0102",
                "start_date": "2020-03-01",
                "end_date": "2020-12-31",
                "member_calculate_type": "01",
                "hours": "200", "amount": 800000,
                "content": "固定50000円の交通費含む"
            },
            "cost_percentage": [
                # {
                #     "project": 36, "project_name": "ANA旅客システム　2019年度開発/ANA　CE基盤", "project_member": 134,
                #     "member_object_id": 18, "member_content_type": 29, "full_name": "南 陽", "start_date": "2020-04-01",
                #     "end_date": "2020-04-30", "year": "2020", "month": "04", "ym": "2020年04月", "organization": 9,
                #     "organization_name": "第三開発部", "cost_percentage_id": None, "percentage": "0.5"
                # },
                # {
                #     "project": "1", "project_name": "システム統合保守（2019年4月～", "project_member": None,
                #     "member_content_type": 29,
                #     "member_object_id": 18, "full_name": "南 陽", "start_date": "2020-04-01", "end_date": "2020-04-30",
                #     "year": "2020", "month": "04", "ym": "2020年04月", "organization": 4, "organization_name": "第三開発部",
                #     "cost_percentage_id": None, "percentage": "0.5"
                # }
            ]
        })

