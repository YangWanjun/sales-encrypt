#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import sourcedefender


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales.settings')

    if 'test' in sys.argv:
        # (1709, 'Index column size too large. The maximum column size is 767 bytes.')を回避するため.
        # この操作はmigrationで新規テーブルを追加する時に発行するCREATE TABLE文の末尾に
        # ROW_FORMAT=DYNAMIC というステートメントを追加するというものです。
        from django.db.backends.mysql.schema import DatabaseSchemaEditor
        DatabaseSchemaEditor.sql_create_table += " ROW_FORMAT=DYNAMIC"

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
