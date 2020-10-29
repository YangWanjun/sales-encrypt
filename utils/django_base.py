import os
import io
import base64
import uuid
import traceback
import datetime
from argparse import RawTextHelpFormatter

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.views.generic.base import View

from utils import common


def blob_to_image(blob, ext):
    with io.BytesIO(blob) as output:
        image = ContentFile(output.getvalue())
        image.name = str(uuid.uuid4()) + (ext or '')
    return image


def base64_to_image(base64_data):
    name_and_ext, data = common.split_base64(base64_data)
    filename = common.get_name_from_base64(name_and_ext) or 'UNKNOWN.png'
    filename, ext = os.path.splitext(filename)
    image = ContentFile(base64.b64decode(data))
    image.name = str(uuid.uuid4()) + (ext or '')
    return image


class BaseBatch(BaseCommand):
    BATCH_NAME = ''
    BATCH_TITLE = ''

    def __init__(self, *args, **kwargs):
        super(BaseBatch, self).__init__(*args, **kwargs)
        self.batch = self.get_batch_manager()
        self.logger = self.batch.get_logger()
        if not self.batch.pk:
            self.batch.title = self.BATCH_TITLE
            self.batch.save()

    def get_batch_manager(self):
        pass

    def handle(self, *args, **options):
        pass

    @transaction.atomic
    def execute(self, *args, **options):
        self.logger.info("============== %s実行開始 ==============" % self.BATCH_TITLE)
        output = None
        try:
            if self.batch.is_active:
                output = super(BaseBatch, self).execute(*args, **options)
            else:
                self.logger.error("%s が有効になっていません。" % (self.BATCH_TITLE,))
        except Exception as ex:
            self.logger.error(ex)
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.info("============== %s実行終了 ==============" % self.BATCH_TITLE)
        return output

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            action='store',
            dest='username',
            default='batch'
        )

    @classmethod
    def get_date_argument(cls, name, **options):
        if name in options:
            if isinstance(options.get(name), datetime.date):
                execute_date = options.get(name)
            else:
                try:
                    execute_date = timezone.localtime().strptime(options.get(name), '%Y-%m-%d').date()
                except Exception as ex:
                    raise ex
        else:
            execute_date = timezone.localtime().date()
        return execute_date

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super(BaseBatch, self).create_parser(prog_name, subcommand, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser


class BaseView(View):
    pass
