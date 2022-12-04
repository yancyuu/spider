# -*- coding: utf-8 -*-

import time
from common_sdk.util.id_generator import generate_common_id
from dao.breeder_da_helper import BreederMessageDAHelper
from manager.manager_base import ManagerBase, ignore_none_param
import proto.spider_entity.breeder_pb2 as breeder_pb


class BreederManager(ManagerBase):
    def __init__(self):
        super().__init__()
        self._da_helper = None

    @property
    def da_helper(self):
        if not self._da_helper:
            self._da_helper = BreederMessageDAHelper()
        return self._da_helper

    @staticmethod
    def create_breeder():
        breeder = breeder_pb.BreederMessage()
        breeder.id = generate_common_id()
        breeder.status = breeder_pb.BreederMessage.BreederStatus.CREATED
        breeder.create_time = int(time.time())
        return breeder

    async def get_breeder(self, id=None):
        return await self.da_helper.get_breeder(id=id)

    def update_breeder(self, breeder, status=None, parse_setting_ids=None, target_url=None, name=None):
        self.__update_status(breeder, status)
        self.__update_name(breeder, name)
        self.__update_target_url(breeder, target_url)
        self.__update_parse_setting_ids(breeder, parse_setting_ids)

    async def list_breeders(self, status=None, name=None):
        breeder = await self.da_helper.list_breeders(
            status=status,
            name=name
        )
        return breeder

    async def delete_breeder(self, breeder):
        self.__update_status(breeder, breeder_pb.BreederStatus.DELETED)

    async def add_or_update_breeder(self, breeder):
        await self.da_helper.add_or_update_breeder(breeder)

    @ignore_none_param
    def __update_status(self, breeder, status):
        if status is None:
            return
        if isinstance(status, str):
            status = breeder_pb.BreederMessage.BreederStatus.Value(status)
        if status == breeder_pb.BreederMessage.BreederStatus.CREATED:
            breeder.create_time = int(time.time())
        elif status == breeder_pb.BreederMessage.BreederStatus.DELETED:
            breeder.delete_time = int(time.time())
        breeder.status = status

    @ignore_none_param
    def __update_target_url(self, breeder, target_url=None):
        breeder.target_url = target_url

    @ignore_none_param
    def __update_name(self, breeder, name=None):
        breeder.name = name

    @ignore_none_param
    def __update_parse_setting_ids(self, breeder, parse_setting_ids=None):
        while breeder.parse_setting_ids:
            breeder.parse_setting_ids.pop()
        for parse_setting_id in parse_setting_ids:
            breeder.parse_setting_ids.append(parse_setting_id)
