import codecs
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection

from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_ddl()
        User.objects.create_user(
            username='admin',
            email='ywjsailor@gmail.com',
            password='admin',
            is_staff=True,
            is_superuser=True,
            first_name='',
            last_name='管理者',
        )
        # with connection.cursor() as cur:
        #     cur.execute('DELETE FROM django_content_type;')
        #     with open('data/test/data/InsertContentType.sql', 'r') as f:
        #         for line in f.readlines():
        #             cur.execute(line)

    @classmethod
    def create_ddl(cls, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, 'data', 'SQL')
        for name in os.listdir(path):
            if not name.lower().endswith('.sql'):
                continue
            with codecs.open(os.path.join(path, name), 'r', 'utf-8') as f:
                sql_list = f.read().split('//')
            with connection.cursor() as cur:
                if len(sql_list) == 1:
                    cur.execute(sql_list[0])
                else:
                    for i, sql in enumerate(sql_list):
                        if sql.strip().upper().startswith('DELIMITER'):
                            continue
                        else:
                            cur.execute(sql)
