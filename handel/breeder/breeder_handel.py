# -*- coding: utf-8 -*-
from common_sdk.logging.logger import logger
from common_sdk.data_transform import protobuf_transformer
from manager.breeder_manager import BreederManager

'''
    用于聚合业务层的操作
'''


class BreederSpiderHandel:

    def __init__(self, actor_id):
        self.actor_id = actor_id
        self.spider_id = actor_id.id
        self.__manager = BreederManager()

    async def list_breeders(self):
        """查询所有的初始爬取规则"""
        return await self.__manager.list_breeders()

    '''
        开始爬取（主要逻辑）
    '''

    async def start_crawling_index(self, data):
        spider_obj = await self.__manager.get_breeder(data.get("id"))
        logger.info("开始爬取 {}".format(protobuf_transformer.protobuf_to_dict(spider_obj)))
        # 根据步骤传配置得到actor中进行处理

    '''
        创建一条固定规则的spider
    '''

    async def generate_breeder(self, data):
        breeder = self.__manager.create_breeder()
        self.__manager.update_breeder(breeder, parse_setting_ids=data.get("parseSettingIds"))
        await self.__manager.add_or_update_breeder(breeder)
        return protobuf_transformer.protobuf_to_dict(breeder)


