import os
import mimetypes
import zipfile
import traceback
import subprocess
import io
import shutil
import sys

from email import encoders
from email.header import Header
from smtplib import SMTPAuthenticationError, SMTPRecipientsRefused

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, get_connection, SafeMIMEText
from django.core.mail.message import MIMEBase
from django.core.validators import validate_email
from django.db import connection
from django.utils.encoding import smart_str

from master.models import EmailLogEntry, Attachment
from utils import constants, common
from utils.app_base import get_sub_tmp_path, get_tmp_file
from utils.errors import CustomException


logger = common.get_system_logger()


class Email(object):
    def __init__(
            self, mail_sender=None,
            mail_to=None, mail_cc=None, mail_bcc=None,
            mail_title=None, mail_body=None,
            pwd_title=None, pwd_body=None,
            attachments=None, is_encrypt=False,
            **kwargs,
    ):
        self.sender = mail_sender
        self.recipient_list = self.str_to_list(mail_to)
        self.cc_list = self.str_to_list(mail_cc)
        self.bcc_list = self.str_to_list(mail_bcc)
        self.attachment_list = self.init_attachments(attachments)
        self.is_encrypt = is_encrypt
        self.mail_title = mail_title
        self.mail_body = mail_body
        self.pwd_title = pwd_title
        self.password = None
        self.pwd_body = pwd_body
        self.temp_files = []

    def check_recipient(self):
        if not self.recipient_list:
            raise CustomException(constants.ERROR_NO_EMAIL_RECIPIENT)
        return self.check_email_address(self.recipient_list)

    def check_cc_list(self):
        return self.check_email_address(self.cc_list)

    def check_bcc_list(self):
        return self.check_email_address(self.bcc_list)

    def check_mail_title(self):
        if not self.mail_title:
            raise CustomException(constants.ERROR_REQUIRE_DATA.format(name='メールの件名'))

    def check_attachment(self):
        if self.attachment_list:
            for attachment in self.attachment_list:
                if not attachment.is_valid():
                    raise CustomException(constants.ERROR_FILE_NOT_FOUND.format(name=attachment.filename))

    @classmethod
    def check_email_address(cls, mail_address):
        if not mail_address:
            return False
        if isinstance(mail_address, str):
            mail_list = [mail_address]
        elif isinstance(mail_address, (tuple, list)):
            mail_list = mail_address
        else:
            raise CustomException(constants.ERROR_INVALID_DATA.format(
                name='メールアドレス', value=mail_address
            ))

        for email in mail_list:
            try:
                validate_email(email)
            except ValidationError:
                raise CustomException(constants.ERROR_INVALID_DATA.format(
                    name='メールアドレス', value=mail_address
                ))
        return True

    @classmethod
    def str_to_list(cls, s):
        if isinstance(s, str):
            return [i.strip() for i in s.split(';') if i]
        else:
            return s
        
    @classmethod
    def init_attachments(cls, attachments):
        if not attachments:
            return []
        attachment_list = []
        for file_uuid in attachments:
            attachment_list.append(AttachmentFile(file_uuid=file_uuid))
        return attachment_list

    @classmethod
    def get_mail_connection(cls):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select value from mst_config where name = %s "
                    " union all "
                    "select value from mst_config where name = %s "
                    " union all "
                    "select value from mst_config where name = %s "
                    " union all "
                    "select value from mst_config where name = %s ",
                    [constants.CONFIG_EMAIL_SMTP_HOST, constants.CONFIG_EMAIL_SMTP_PORT,
                     constants.CONFIG_EMAIL_ADDRESS, constants.CONFIG_EMAIL_PASSWORD]
                )
                host, port, username, password = cursor.fetchall()
            backend = get_connection()
            backend.host = str(host[0])
            backend.port = int(port[0])
            backend.username = str(username[0])
            backend.password = str(password[0])
            return backend
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise CustomException(constants.ERROR_CONFIG_EMAIL_SERVER)

    def zip_attachments(self):
        if self.attachment_list:
            if sys.platform in ("linux", "linux2"):
                # tmpフォルダー配下の一時フォルダーを取得する
                tmp_path = get_sub_tmp_path()
                self.temp_files.append(tmp_path)
                tmp_zip = get_tmp_file('zip')
                self.temp_files.append(tmp_zip)
                # 添付ファイルを一時フォルダーにコピーする
                for attachment_file in self.attachment_list:
                    new_path = os.path.join(tmp_path, attachment_file.filename)
                    self.temp_files.append(new_path)
                    if attachment_file.is_bytes():
                        # バイナリーファイルを一時ファイルに書き込む
                        with open(new_path, 'wb') as f:
                            f.write(attachment_file.content)
                    else:
                        shutil.copy(attachment_file.filepath, new_path)
                password = self.generate_password()
                # tmpフォルダー配下すべてのファイル名をUTF8からShift-JISに変換する
                subprocess.call(["convmv", "-r", "-f", "utf8", '-t', 'sjis', '--notest', tmp_path.rstrip('/') + '/'])
                # 一時フォルダーを圧縮する
                command = "zip --password {0} -j {1} {2}/*".format(password, tmp_zip, tmp_path.rstrip('/'))
                subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                bytes_data = open(tmp_zip, 'rb', ).read()
                return bytes_data
            else:
                buff = io.BytesIO()
                in_memory_zip = zipfile.ZipFile(buff, mode='w')
                for attachment_file in self.attachment_list:
                    if attachment_file.is_bytes():
                        in_memory_zip.writestr(attachment_file.filename, attachment_file.content)
                    else:
                        in_memory_zip.write(attachment_file.filename, attachment_file.filename)
                in_memory_zip.close()
                return buff.getvalue()
        else:
            return None

    # def escape(self, name):
    #     """Shift_JISのダメ文字対策
    #
    #     2バイト目に「5C」のコードが使われている文字は、次のようなものがあります。
    #     ―ソЫⅨ噂浬欺圭構蚕十申曾箪貼能表暴予禄兔喀媾彌拿杤歃濬畚秉綵臀藹觸軆鐔饅鷭偆砡
    #
    #     :param name:
    #     :return:
    #     """
    #     chars = "ソЫⅨ噂浬欺圭構蚕十申曾箪貼能表暴予禄兔喀媾彌拿杤歃濬畚秉綵臀藹觸軆鐔饅鷭偆砡"
    #     s = name
    #     for c in chars:
    #         if c in s:
    #             s = s.replace(c, "＿")
    #     return s

    def generate_password(self, length=8):
        self.password = common.generate_password(length)
        return self.password

    def send_email(self, user=None):
        try:
            self.check_mail_title()
            self.check_recipient()
            self.check_cc_list()
            self.check_bcc_list()
            self.check_attachment()

            mail_connection = self.get_mail_connection()
            if not self.sender:
                self.sender = mail_connection.username

            email = EmailMultiAlternativesWithEncoding(
                subject=self.mail_title,
                body=self.mail_body,
                from_email=self.sender,
                to=self.recipient_list,
                cc=self.cc_list,
                bcc=self.bcc_list,
                connection=mail_connection
            )
            # email.attach_alternative(self.mail_body, constants.MIME_TYPE_HTML)
            if self.is_encrypt is False:
                for attachment in [item for item in self.attachment_list]:
                    if attachment.is_bytes():
                        email.attach(attachment.filename, attachment.content, constants.MIME_TYPE_ZIP)
                    else:
                        email.attach_file(attachment.filepath, constants.MIME_TYPE_STREAM)
            else:
                attachments = self.zip_attachments()
                if attachments:
                    email.attach('%s.zip' % self.mail_title, attachments, constants.MIME_TYPE_ZIP)
            email.send()
            # パスワードを送信する。
            self.send_password(mail_connection, user=user)
            logger.info(constants.INFO_EMAIL_SENT.format(
                title=self.mail_title,
                to=';'.join(self.recipient_list) if self.recipient_list else '',
                cc=';'.join(self.cc_list) if self.cc_list else '',
                bcc=';'.join(self.bcc_list) if self.bcc_list else '',
            ))

            if user:
                # 送信ログ
                if self.attachment_list:
                    attachment_name = ";".join([item.filename for item in self.attachment_list])
                else:
                    attachment_name = None
                EmailLogEntry.objects.create(
                    user=user,
                    sender=self.sender,
                    recipient=";".join(self.recipient_list),
                    cc=";".join(self.cc_list) if self.cc_list else None,
                    bcc=";".join(self.bcc_list) if self.bcc_list else None,
                    title=self.mail_title,
                    body=self.mail_body,
                    attachments=attachment_name,
                )
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
            logger.error(traceback.format_exc())
            raise e
        except SMTPAuthenticationError:
            raise CustomException(constants.ERROR_EMAIL_AUTHENTICATION)
        except SMTPRecipientsRefused:
            raise CustomException(constants.ERROR_EMAIL_AUTHENTICATION)
        except Exception as ex:
            logger.error(str(traceback.format_exc()))
            raise ex
        finally:
            # # 一時ファイルを削除
            # for path in self.temp_files:
            #     if os.path.exists(path):
            #         if os.path.isdir(path):
            #             shutil.rmtree(path)
            #         else:
            #             os.remove(path)
            pass

    def send_password(self, conn, user=None):
        if self.attachment_list and self.is_encrypt and self.password:
            subject = self.pwd_title or self.mail_title
            try:
                body = self.pwd_body.format(password=self.password)
            except Exception as ex:
                logger.error(ex)
                body = "PW: %s" % self.password
            email = EmailMultiAlternativesWithEncoding(
                subject=subject,
                body=body,
                from_email=self.sender,
                to=self.recipient_list,
                cc=self.cc_list,
                connection=conn
            )
            # email.attach_alternative(body, constants.MIME_TYPE_HTML)
            email.send()
            logger.info(constants.INFO_PASSWORD_SENT.format(title=self.mail_title))
            if user:
                # パスワード送信ログ
                EmailLogEntry.objects.create(
                    user=user,
                    sender=self.sender,
                    recipient=";".join(self.recipient_list),
                    cc=";".join(self.cc_list) if self.cc_list else None,
                    bcc=";".join(self.bcc_list) if self.bcc_list else None,
                    title=subject,
                    body=body,
                    attachments=None,
                )


class AttachmentFile:

    def __init__(self, file_uuid=None, content=None, filename=None):
        self.content = content
        if file_uuid:
            tmp_attachment = Attachment.get_by_uuid(file_uuid) 
            self.filename = tmp_attachment.name if tmp_attachment else None
            self.filepath = tmp_attachment.path.path if tmp_attachment and tmp_attachment.path else None
        else:
            self.filename = filename
            self.filepath = None

    def is_valid(self):
        """有効なファイルであるかどうか

        :return:
        """
        if self.filepath:
            return os.path.exists(self.filepath)
        elif self.content and isinstance(self.content, bytes):
            return True
        else:
            return False

    def is_bytes(self):
        if self.content and isinstance(self.content, bytes):
            return True
        else:
            return False


class EmailMultiAlternativesWithEncoding(EmailMultiAlternatives):
    def _create_attachment(self, filename, content, mimetype=None):
        """
        Converts the filename, content, mimetype triple into a MIME attachment
        object. Use self.encoding when handling text attachments.
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            # if mimetype is None:
            #     mimetype = constants.MIME_TYPE_EXCEL
        basetype, subtype = mimetype.split('/', 1)
        if basetype == 'text':
            encoding = self.encoding or settings.DEFAULT_CHARSET
            attachment = SafeMIMEText(smart_str(content, settings.DEFAULT_CHARSET), subtype, encoding)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            encoders.encode_base64(attachment)
        if filename:
            try:
                filename = Header(filename, 'utf-8').encode()
            except Exception as ex:
                logger.error(ex)
                logger.error(traceback.format_exc())
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        return attachment
