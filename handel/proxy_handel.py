# -*- coding: utf-8 -*-
import json
import time
from common_sdk.logging.logger import logger
from common_sdk.data_transform import protobuf_transformer
from manager.notification_manager import NotificationManager
import task_common.proto.notification.notification_pb2 as notification_pb
from proxy.message_service_proxy import MessageServiceProxy

'''
    用于生成代理的handel
'''


class ProxyHandel:

    def __init__(self, actor_id):
        self.actor_id = actor_id
        self.proxy_id = actor_id.id
        self.__load_time = None

    async def get_cookie(self, event_body):
        # 把信息存到数据库并发送
        # 根据创建一个将要发送的消息
        message = await self.generate_message(event_body)

    '''
        创建一条普通cookie
    '''

    async def generate_message(self, event_body):
        message_manager = NotificationManager()
        message = notification_pb.NotificationMessage()
        message_manager.create_notification(message)
        # 将type更新到message的type
        type = event_body["type"]
        del event_body["type"]
        message.event_body = json.dumps(event_body)
        message_manager.update_notification(message, type=type, target_id=self.proxy_id)
        await message_manager.add_or_update_notification(message)
        return message
