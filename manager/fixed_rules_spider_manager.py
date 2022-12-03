# -*- coding: utf-8 -*-

import time
from common_sdk.util.id_generator import generate_common_id
from dao.fixed_rules_spider_da_helper import FixedRulesSpiderMessageDAHelper
from manager.manager_base import ManagerBase, ignore_none_param
import proto.spider_entity.fixed_rules_spider_pb2 as fixed_rules_spider_pb


class FixedRulesSpiderMessageManager(ManagerBase):
    def __init__(self):
        super().__init__()
        self._da_helper = None

    @property
    def da_helper(self):
        if not self._da_helper:
            self._da_helper = FixedRulesSpiderMessageDAHelper()
        return self._da_helper

    @staticmethod
    def create_fixed_rules_spider():
        fixed_rules_spider = fixed_rules_spider_pb.FixedRulesSpiderMessage()
        fixed_rules_spider.id = generate_common_id()
        fixed_rules_spider.status = fixed_rules_spider_pb.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus.CREATED
        fixed_rules_spider.create_time = int(time.time())
        return fixed_rules_spider

    async def get_fixed_rules_spider(self, id=None):
        return await self.da_helper.get_fixed_rules_spider(id=id)

    def update_fixed_rules_spider(self, fixed_rules_spider, status=None, parse_setting_ids=None, target_url=None, name=None):
        self.__update_status(fixed_rules_spider, status)
        self.__update_name(fixed_rules_spider, name)
        self.__update_target_url(fixed_rules_spider, target_url)
        self.__update_parse_setting_ids(fixed_rules_spider, parse_setting_ids)

    async def list_fixed_rules_spiders(self, status=None, name=None):
        fixed_rules_spiders = await self.da_helper.list_fixed_rules_spiders(
            status=status,
            name=name
        )
        return fixed_rules_spiders

    async def delete_fixed_rules_spiders(self, fixed_rules_spider):
        self.__update_status(fixed_rules_spider, fixed_rules_spider_pb.FixedRulesSpiderMessageStatus.DELETED)

    async def add_or_update_fixed_rules_spider(self, fixed_rules_spider):
        await self.da_helper.add_or_update_fixed_rules_spider(fixed_rules_spider)

    @ignore_none_param
    def __update_status(self, fixed_rules_spider, status):
        if status is None:
            return
        if isinstance(status, str):
            status = fixed_rules_spider_pb.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus.Value(status)
        if status == fixed_rules_spider_pb.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus.CREATED:
            fixed_rules_spider.create_time = int(time.time())
        elif status == fixed_rules_spider_pb.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus.DELETED:
            fixed_rules_spider.delete_time = int(time.time())
        fixed_rules_spider.status = status

    @ignore_none_param
    def __update_target_url(self, fixed_rules_spider, target_url=None):
        fixed_rules_spider.target_url = target_url

    @ignore_none_param
    def __update_name(self, fixed_rules_spider, name=None):
        fixed_rules_spider.v = name

    @ignore_none_param
    def __update_parse_setting_ids(self, fixed_rules_spider, parse_setting_ids=None):
        while fixed_rules_spider.parse_setting_ids:
            fixed_rules_spider.parse_setting_ids.pop()
        for parse_setting_id in parse_setting_ids:
            fixed_rules_spider.parse_setting_ids.append(parse_setting_id)
