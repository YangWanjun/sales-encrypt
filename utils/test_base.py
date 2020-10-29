from django.contrib.auth.models import User
from django.db import connection

from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):
    fixtures = [
        'data/test/fixtures/Company.json',
        'data/test/fixtures/Member.json',
        'data/test/fixtures/Contract.json',
        'data/test/fixtures/ContractAllowance.json',
        'data/test/fixtures/ContractComment.json',
        'data/test/fixtures/Organizations.json',
        'data/test/fixtures/OrganizationMember.json',
        'data/test/fixtures/Salesperson.json',
        'data/test/fixtures/ClientCompany.json',
        'data/test/fixtures/ProjectBusinessType.json',
    ]

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username='admin',
            email='yang.wanjun@wisdom-technology.co.jp',
            password='admin',
            is_staff=True,
            is_superuser=True,
            first_name='ユーザー',
            last_name='テスト',
        )
        with connection.cursor() as cur:
            cur.execute('DELETE FROM django_content_type;')
            with open('data/test/data/InsertContentType.sql', 'r') as f:
                for line in f.readlines():
                    cur.execute(line)
