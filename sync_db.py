import os
import sys
import django
from django.core.management import call_command
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sales.settings")
django.setup()


def main(argv):
    if '-f' in argv:
        remove_files_only = True
    else:
        remove_files_only = False

    del_migration_files()
    if remove_files_only is False:
        del_migration_records()
        migrate()


def migrate():
    call_command('migrate', '--fake')
    call_command('makemigrations')
    call_command('migrate', '--fake')


def del_migration_records():
    with connection.cursor() as cursor:
        cnt = cursor.execute("delete from django_migrations")
        print('EXEC: delete from django_migrations. %s rows deleted' % cnt)


def del_migration_files():
    root_path = os.path.dirname(os.path.realpath(__file__))
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            if filename in ('__init__.py', '__init__.pyc'):
                continue
            if os.path.basename(root) == 'migrations':
                path = os.path.join(root, filename)
                os.remove(path)
                print('DEL: %s' % path)


if __name__ == '__main__':
    main(sys.argv[1:])
