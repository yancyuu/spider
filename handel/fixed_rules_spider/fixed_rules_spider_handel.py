# -*- coding: utf-8 -*-
from common_sdk.logging.logger import logger
from common_sdk.data_transform import protobuf_transformer
from manager.fixed_rules_spider_manager import FixedRulesSpiderMessageManager

'''
    用于聚合业务层的操作
'''


class FixedRulesSpiderHandel:

    def __init__(self, actor_id):
        self.actor_id = actor_id
        self.spider_id = actor_id.id
        self.__manager = FixedRulesSpiderMessageManager()

    async def list_fixed_rules_spiders(self):
        """查询所有的初始爬取规则"""
        return await self.__manager.list_fixed_rules_spiders()

    '''
        开始爬取（主要逻辑）
    '''

    async def start_crawling_index(self, data):
        spider_obj = await self.__manager.get_fixed_rules_spider(data.get("id"))
        logger.info("开始爬取 {}".format(protobuf_transformer.protobuf_to_dict(spider_obj)))
        # 根据步骤传配置得到actor中进行处理

    '''
        创建一条固定规则的spider
    '''

    async def generate_fixed_rules_spider(self, data):
        fixed_rules_spider = self.__manager.create_fixed_rules_spider()
        self.__manager.update_fixed_rules_spider(fixed_rules_spider,
                                                 spider=data.get("spider"),
                                                 parse_settings=data.get("parseSettings"))
        await self.__manager.add_or_update_fixed_rules_spider(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)


