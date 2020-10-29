import os
import firebase_admin
from firebase_admin import credentials, messaging

from django.conf import settings

from utils import common, constants

logger = common.get_system_logger()


cred = credentials.Certificate(os.path.join(
    settings.BASE_DIR,
    'data',
    'sales-yang-firebase-adminsdk-2ga7e-17745491f0.json'
))
firebase_admin.initialize_app(credential=cred)


# def subscribe_to_topic(registration_tokens, topic):
#     """トピックにデバイスを登録する。
#
#     :param registration_tokens: Instance IDリスト
#     :param topic: トピック名称
#     :return:
#     """
#     res = messaging.subscribe_to_topic(registration_tokens, topic)
#     return res.success_count, res.failure_count, res.errors
#
#
# def unsubscribe_from_topic(registration_tokens, topic):
#     """トピックにデバイスの登録を解除する。
#
#     :param registration_tokens: Instance IDリスト
#     :param topic: トピック名称
#     :return:
#     """
#     res = messaging.unsubscribe_from_topic(registration_tokens, topic)
#     return res.success_count, res.failure_count, res.errors


def send_message_to_topic(topic, title, body, forward=None):
    """ユーザーにメッセージを通知する
    メッセージを先にＤＢ登録してから通知します、
    そうしないと画面の通知一覧にメッセージが表示できない場合があります。

    :param topic: マスターに登録済のトピック（Firebaseに登録済のトピックではありません）
    :param title: タイトル
    :param body: メッセージ内容
    :param forward: メッセージを押下後の遷移先
    :return:
    """
    from account.models import Notification
    from master.models import FirebaseDevice
    Notification.add_by_topic(topic.name, title, body, forward=forward)
    devices = FirebaseDevice.objects.filter(user__in=topic.users.all())
    if devices.count() == 0:
        # トピックに登録したデバイスがない場合
        logger.info(constants.INFO_FIREBASE_NO_DEVICE.format(topic=topic.name))
        return
    # ユーザーに通知する
    message = messaging.MulticastMessage(data={
        'title': title,
        'body': body
    }, tokens=[item.token for item in devices])

    res = messaging.send_multicast(message)
    logger.info(constants.INFO_FIREBASE_SEND_MESSAGE.format(topic=topic.name))
