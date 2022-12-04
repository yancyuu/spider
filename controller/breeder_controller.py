# -*- coding: utf-8 -*-

from controller.controller_base import ControllerBase
from common_sdk.data_transform import protobuf_transformer
from service import errors
from spider_sdk.client.actor_proxy_client import ActorProxyClient
from manager.breeder_manager import BreederManager


class BreederController(ControllerBase):
    @property
    def manager(self):
        if not self._manager:
            self._manager = BreederManager()
        return self._manager

    def __init__(self, req):
        super().__init__(req)
        self._OP_FUNC_MAP.update({})
        self._manager = None

    async def get(self):
        breeder = await self.manager.get_breeder(
            id=await self.get_json_param("id"),
        )
        if not breeder:
            return None
        return protobuf_transformer.protobuf_to_dict(breeder)

    async def create(self):
        name = await self.get_json_param("name")
        if await self.manager.list_breeders(name=name):
            raise errors.CustomMessageError("已经有此名称spider")
        breeder = self.manager.create_breeder()
        # 在中台创建配置
        spider_setting_proxy_client = ActorProxyClient(breeder.id).spider_setting_actor_proxy()
        parse_settings = await self.get_json_param("parseSettings", [])
        if not parse_settings:
            return
        parse_setting_ids = []
        for parse_setting in parse_settings:
            setting = await spider_setting_proxy_client.GenerateParseSettings(parse_setting)
            if not setting:
                continue
            parse_setting_ids.append(setting.get("id"))
        self.manager.update_breeder(
            breeder,
            name=await self.get_json_param("name"),
            target_url=await self.get_json_param("targetUrl"),
            parse_setting_ids=parse_setting_ids
        )
        await self.manager.add_or_update_breeder(breeder)
        return protobuf_transformer.protobuf_to_dict(breeder)

    async def delete(self):
        breeder = await self.manager.get_breeder(
            id=self.get_json_param("id"),
        )
        if breeder is None:
            raise errors.CustomMessageError("定向爬虫不存在")
        await self.manager.delete_breeders(breeder)
        await self.manager.add_or_update_breeder(breeder)
        return protobuf_transformer.protobuf_to_dict(breeder)

    async def update(self):
        breeder = await self.manager.get_breeder(
            id=await self.get_json_param("id"),
        )
        if breeder is None:
            raise errors.CustomMessageError("定向爬虫不存在")
        if await self.get_json_param("parseSetting"):
            spider_setting_proxy_client = ActorProxyClient(breeder.id).spider_setting_actor_proxy()
            res = await spider_setting_proxy_client.UpdateParseSetting(await self.get_json_param("parseSetting"))
            if res.get("errcode") != 0:
                raise errors.Error((res.get("errcode"), res.get("errmsg")))
        self.manager.update_breeder(
            breeder,
            status=await self.get_json_param("status"),
            parse_setting_ids=await self.get_json_param("parseSettingIds"),
            target_url=await self.get_json_param("targetUrl"),
        )
        await self.manager.add_or_update_breeder(breeder)
        return protobuf_transformer.protobuf_to_dict(breeder)

    async def list(self):
        breeders = await self.manager.list_breeders(
            status=await self.get_json_param("status")
        )
        breeders = protobuf_transformer.batch_protobuf_to_dict(breeders)
        data = []
        for breeder in breeders:
            # 查找配置
            spider_setting_proxy_client = ActorProxyClient(breeder['id']).spider_setting_actor_proxy()
            res = await spider_setting_proxy_client.ListParseSettings({"ids": breeder["parseSettingIds"]})
            if res.get("errcode") != 0:
                continue
            breeder["parseSettings"] = res.get("data")
            data.append(breeder)
        return data
