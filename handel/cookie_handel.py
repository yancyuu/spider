# -*- coding: utf-8 -*-
import json
import time
from common_sdk.logging.logger import logger
from common_sdk.data_transform import protobuf_transformer
from manager.cookie_manager import CookieManager
import proto.cookie_pb2 as cookie_pb

'''
    用于生成cookie的handel
'''


class CookieHandel:

    def __init__(self, actor_id):
        self.actor_id = actor_id
        self.cookie_id = actor_id.id
        self.__load_time = None

    async def get_cookie(self):
        # 根据创建一个将要发送的消息
        cookie_manager = CookieManager()
        # 查询所有的cookie
        cookie_list = await cookie_manager.list_cookies()
        # 打乱顺序

    '''
        创建一条普通cookie
    '''

    @staticmethod
    async def generate_cookie():
        cookie_map = ""
        cookie_manager = CookieManager()
        cookie = cookie_pb.CookieMessage()
        cookie_manager.create_cookie(cookie, cookie_map)
        await cookie_manager.add_or_update_cookie(cookie)
        return cookie
