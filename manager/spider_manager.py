# -*- coding: utf-8 -*-

import time
from common_sdk.util.id_generator import generate_common_id
from dao.spider_da_helper import SpiderDAHelper
from manager.manager_base import ManagerBase
import spider.proto.spider_pb2 as spider_pb


class SpiderManager(ManagerBase):
    def __init__(self):
        super().__init__()
        self._da_helper = None

    @property
    def da_helper(self):
        if not self._da_helper:
            self._da_helper = SpiderDAHelper()
        return self._da_helper

    @staticmethod
    def create_spider(spider, url=None):
        if url is None:
            return
        spider.id = generate_common_id()
        spider.url = url
        spider.status = spider_pb.SpiderMessage.SpiderStatus.NONE
        spider.create_time = int(time.time())
        return spider

    async def get_spider(self, id=None):
        return await self.da_helper.get_spider(id=id)

    def update_spider(self, spider, status=None, request=None, response=None):
        self.__update_status(spider, status)
        self.__update_request(spider, request)
        self.__update_response(spider, response)

    async def list_spiders(self, status=None):
        spiders = await self.da_helper.list_spiders(
            status=status
        )
        return spiders

    async def list_not_confirmed_spiders(self, ids=None, target_id=None):
        return await self.da_helper.list_not_confirmed_spiders(ids, target_id)

    async def add_or_update_spider(self, spider):
        await self.da_helper.add_or_update_spider(spider)

    @staticmethod
    def __update_status(spider, status):
        if status is None:
            return
        if isinstance(status, str):
            status = spider_pb.SpiderMessage.SpiderStatus.Value(status)
        if status == spider_pb.SpiderMessage.SpiderStatus.RETRY:
            spider.retry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        elif status == spider_pb.SpiderMessage.SpiderStatus.PARSED:
            spider.parse_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        spider.status = status

    @staticmethod
    def __update_request(spider, request):
        if request is None:
            return
        spider.request = request

    @staticmethod
    def __update_response(spider, response):
        if response is None:
            return
        spider.response = response





