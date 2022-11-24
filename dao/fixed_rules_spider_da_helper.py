# -*- coding: utf-8 -*-

import proto.spider_entity.fixed_rules_spider_pb2 as fixed_rules_spider_pb

from dao.constants import DBConstants
from dao.mongodb_dao_helper import MongodbClientHelper
from common_sdk.data_transform import protobuf_transformer


class FixedRulesSpiderMessageDAHelper(MongodbClientHelper):
    def __init__(self):
        db = DBConstants.MONGODB_SPIDER_DB_NAME
        coll = DBConstants.SPIDER_ENTITY_COLLECTION_NAME
        super().__init__(db, coll)

    @property
    def _fixed_rules_spider_collection(self):
        return self

    async def add_or_update_fixed_rules_spider(self, fixed_rules_spider):
        matcher = {"id": fixed_rules_spider.id}
        json_data = protobuf_transformer.protobuf_to_dict(fixed_rules_spider)
        await self._fixed_rules_spider_collection.do_replace(matcher, json_data, upsert=True)

    async def get_fixed_rules_spider(self, id=None):
        matcher = {}
        self.__set_matcher_id(matcher, id)
        self.__set_matcher_not_delete_status(matcher)
        if not matcher:
            return
        fixed_rules_spider = await self._fixed_rules_spider_collection.find_one(matcher)
        return protobuf_transformer.dict_to_protobuf(fixed_rules_spider, fixed_rules_spider_pb.FixedRulesSpiderMessage)

    async def list_fixed_rules_spiders(self, status=None):
        matcher = {}
        self.__set_matcher_status(matcher, status)
        self.__set_matcher_not_delete_status(matcher)
        if not matcher:
            return []
        fixed_rules_spiders = await self._fixed_rules_spider_collection.find(matcher)
        return protobuf_transformer.batch_protobuf_to_dict(fixed_rules_spiders)

    @staticmethod
    def __set_matcher_ids(matcher, ids):
        if ids is None:
            return
        matcher.update({"id": {"$in": ids}})

    @staticmethod
    def __set_matcher_id(matcher, id):
        if id is None:
            return
        matcher.update({"id": id})

    @staticmethod
    def __set_matcher_status(matcher, status):
        if status is None:
            return
        if isinstance(status, str):
            matcher.update({"status": status})
        elif isinstance(status, fixed_rules_spider_pb.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus):
            matcher.update({"status": fixed_rules_spider_pb.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus.Name(status)})
        matcher.update({"status": status})

    @staticmethod
    def __set_matcher_not_delete_status(matcher):
        matcher.update({"status": {"$ne": "DELETED"}})

