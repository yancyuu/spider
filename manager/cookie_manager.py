# -*- coding: utf-8 -*-

import time
from common_sdk.util.id_generator import generate_common_id
from dao.cookie_da_helper import CookieDAHelper
from manager.manager_base import ManagerBase
import proto.cookie_pb2 as cookie_pb


class CookieManager(ManagerBase):
    def __init__(self):
        super().__init__()
        self._da_helper = None

    @property
    def da_helper(self):
        if not self._da_helper:
            self._da_helper = CookieDAHelper()
        return self._da_helper

    @staticmethod
    def create_cookie(cookie, cookie_map=None):
        if cookie is None:
            return
        cookie.id = generate_common_id()
        cookie.cookie_map = cookie_map
        cookie.status = cookie_pb.CookieMessage.cookieStatus.NONE
        cookie.create_time = int(time.time())
        return cookie

    async def get_cookie(self, id=None):
        return await self.da_helper.get_cookie(id=id)

    def update_cookie(self, cookie, status=None):
        self.__update_status(cookie, status)

    async def list_cookies(self, status=None):
        cookies = await self.da_helper.list_cookies(
            status=status
        )
        return cookies

    async def list_not_confirmed_cookies(self, ids=None, target_id=None):
        return await self.da_helper.list_not_confirmed_cookies(ids, target_id)

    async def add_or_update_cookie(self, cookie):
        await self.da_helper.add_or_update_cookie(cookie)

    @staticmethod
    def __update_status(cookie, status):
        if status is None:
            return
        if isinstance(status, str):
            status = cookie_pb.CookieMessage.CookieStatus.Value(status)
        if status == cookie_pb.CookieMessage.CookieStatus.USED:
            cookie.use_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        cookie.status = status






