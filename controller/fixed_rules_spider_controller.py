# -*- coding: utf-8 -*-

from controller.controller_base import ControllerBase
from common_sdk.data_transform import protobuf_transformer
from service import errors
from spider_sdk.client.actor_proxy_client import ActorProxyClient
from manager.fixed_rules_spider_manager import FixedRulesSpiderMessageManager


class FixedRulesSpiderController(ControllerBase):
    @property
    def manager(self):
        if not self._manager:
            self._manager = FixedRulesSpiderMessageManager()
        return self._manager

    def __init__(self, req):
        super().__init__(req)
        self._OP_FUNC_MAP.update({})
        self._manager = None

    async def get(self):
        id = await self.get_json_param("id")
        fixed_rules_spider = await self.manager.get_fixed_rules_spider(
            id=id,
        )
        if not fixed_rules_spider:
            return None
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    async def create(self):
        name = await self.get_json_param("name")
        if await self.manager.list_fixed_rules_spiders(name=name):
            raise errors.CustomMessageError("已经有此名称spider")
        fixed_rules_spider = self.manager.create_fixed_rules_spider()
        # 在中台创建配置
        spider_setting_proxy_client = ActorProxyClient(fixed_rules_spider.id).spider_setting_actor_proxy()
        parse_settings = await self.get_json_param("parseSettings", [])
        if not parse_settings:
            return
        parse_setting_ids = []
        for parse_setting in parse_settings:
            setting = await spider_setting_proxy_client.GenerateParseSettings(parse_setting)
            if not setting:
                continue
            parse_setting_ids.append(setting.get("id"))
        self.manager.update_fixed_rules_spider(
            fixed_rules_spider,
            name=await self.get_json_param("name"),
            target_url=await self.get_json_param("targetUrl"),
            parse_setting_ids=parse_setting_ids
        )
        await self.manager.add_or_update_fixed_rules_spider(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    async def delete(self):
        fixed_rules_spider = await self.manager.get_fixed_rules_spider(
            id=self.get_json_param("id"),
        )
        if fixed_rules_spider is None:
            raise errors.CustomMessageError("定向爬虫不存在")
        await self.manager.delete_fixed_rules_spiders(fixed_rules_spider)
        await self.manager.add_or_update_fixed_rules_spider(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    async def update(self):
        fixed_rules_spider = await self.manager.get_fixed_rules_spider(
            id=await self.get_json_param("id"),
        )
        if fixed_rules_spider is None:
            raise errors.CustomMessageError("定向爬虫不存在")
        if await self.get_json_param("parseSetting"):
            spider_setting_proxy_client = ActorProxyClient(fixed_rules_spider.id).spider_setting_actor_proxy()
            res = await spider_setting_proxy_client.UpdateParseSetting(await self.get_json_param("parseSetting"))
            if res.get("errcode") != 0:
                raise errors.Error((res.get("errcode"), res.get("errmsg")))
        self.manager.update_fixed_rules_spider(
            fixed_rules_spider,
            status=await self.get_json_param("status"),
            parse_setting_ids=await self.get_json_param("parseSettingIds"),
            target_url=await self.get_json_param("targetUrl"),
        )
        await self.manager.add_or_update_fixed_rules_spider(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    async def list(self):
        fixed_rules_spiders = await self.manager.list_fixed_rules_spiders(
            status=self.get_json_param("status")
        )
        fixed_rules_spiders = protobuf_transformer.batch_protobuf_to_dict(fixed_rules_spiders)
        data= []
        for fixed_rules_spider in fixed_rules_spiders:
            # 查找配置
            spider_setting_proxy_client = ActorProxyClient(fixed_rules_spider.id).spider_setting_actor_proxy()
            res = await spider_setting_proxy_client.ListParseSetting({"ids": fixed_rules_spider["parseSettingIds"]})
            if res.get("errcode") != 0:
                continue
            fixed_rules_spider["parseSettings"] = res.get("data")
            data.append(fixed_rules_spider)
        return data
