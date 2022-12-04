# -*- coding: utf-8 -*-

import proto.spider_entity.breeder_pb2 as breeder_pb

from dao.constants import DBConstants
from dao.mongodb_dao_helper import MongodbClientHelper
from common_sdk.data_transform import protobuf_transformer


class BreederMessageDAHelper(MongodbClientHelper):
    def __init__(self):
        db = DBConstants.MONGODB_SPIDER_DB_NAME
        coll = DBConstants.SPIDER_ENTITY_COLLECTION_NAME
        super().__init__(db, coll)

    @property
    def _breeder_collection(self):
        return self

    async def add_or_update_breeder(self, breeder):
        matcher = {"id": breeder.id}
        json_data = protobuf_transformer.protobuf_to_dict(breeder)
        await self._breeder_collection.do_replace(matcher, json_data, upsert=True)

    async def get_breeder(self, id=None):
        matcher = {}
        self.__set_matcher_id(matcher, id)
        self.__set_matcher_not_delete_status(matcher)
        if not matcher:
            return
        breeder = await self._breeder_collection.find_one(matcher)
        return protobuf_transformer.dict_to_protobuf(breeder, breeder_pb.BreederMessage)

    async def list_breeders(self, status=None, name=None):
        matcher = {}
        self.__set_matcher_status(matcher, status)
        self.__set_matcher_name(matcher, name)
        self.__set_matcher_not_delete_status(matcher)
        print("---->{}".format(matcher))
        if not matcher:
            return []
        breeders = await self._breeder_collection.find(matcher)
        return protobuf_transformer.batch_dict_to_protobuf(breeders, breeder_pb.BreederMessage)

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
        matcher.update({"status": status})

    @staticmethod
    def __set_matcher_name(matcher, name):
        if name is None:
            return
        matcher.update({"name": name})

    @staticmethod
    def __set_matcher_not_delete_status(matcher):
        matcher.update({"status": {"$ne": "DELETED"}})

