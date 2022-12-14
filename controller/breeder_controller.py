# -*- coding: utf-8 -*-

from controller.controller_base import ControllerBase
from common_sdk.data_transform import protobuf_transformer
from service import errors
from spider_sdk.client.actor_proxy_client import ActorProxyClient
from spider_sdk.client.breeder_client import BreederClient
from spider_sdk.builder.breeder_builder import BreederBuilder
from manager.breeder_manager import BreederManager
from lxml import etree


class BreederController(ControllerBase):
    @property
    def manager(self):
        if not self._manager:
            self._manager = BreederManager()
        return self._manager

    def __init__(self, req):
        super().__init__(req)
        self.spider_setting_proxy_client = None
        self._breeder_builder = None
        self._OP_FUNC_MAP.update({
            "start_reproduce": self.start_reproduce
        })
        self._manager = None

    @property
    def breeder_builder(self):
        if self._breeder_builder is None:
            self._breeder_builder = BreederBuilder()
        return self._breeder_builder

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

    async def start_reproduce(self):
        id = await self.get_json_param("id")
        if not id:
            raise errors.CustomMessageError("未输入爬虫id")
        breeder = protobuf_transformer.protobuf_to_dict(await self.manager.get_breeder(id=id))
        await self.__start_parse_by_setting(breeder=breeder)

    async def __start_parse_by_setting(self, breeder=None):
        if not breeder:
            raise errors.CustomMessageError("此爬虫被删除或者不存在")
        # 查找配置
        self.spider_setting_proxy_client = ActorProxyClient(breeder['id']).spider_setting_actor_proxy()
        res = await self.spider_setting_proxy_client.ListParseSettings({"ids": breeder["parseSettingIds"]})
        print("setting--->{}".format(res))
        if res.get("errcode") != 0 or res.get("data") is None:
            return
        parse_settings = res.get("data")
        if not parse_settings:
            return
        index_url = breeder["targetUrl"]
        # 发起一个请求
        self.breeder_builder.url = index_url
        response = await BreederClient().get(self.breeder_builder)
        print("response--->{}".format(response))

        # 1. 取第一个配置作为此爬虫的初始配置
        index_setting = parse_settings[0]
        # 2. 查看这个配置有无下一页：若有则复制出匹配上规则的爬虫
        print("index_setting--->{}".format(index_setting))

        await self.__create_spider_by_next_page(index_url, index_setting, response)
        # 3. 根据此初始配置进行解析
        await self.__parse_spider(index_setting, response)

    async def __create_spider_by_next_page(self, index_url, index_setting, response):
        """
            用于通过配置来生成爬虫
        :param index_url: 母体爬虫url
        :param index_setting: 此爬虫应用的当前配置
        :param response: 此页面返回
        :return:
        """
        if index_setting.get("nextSpiderRules") and index_setting.get("parseType") == "XPATH":
            doc = etree.HTML(response.text)
            next_page_urls = doc.xpath(index_setting.get("nextSpiderRules"))
            # 繁殖新爬虫，url为下一页，配置为相同配置
            for next_page_url in next_page_urls:
                if next_page_url == index_url:
                    continue
                breeder = self.manager.create_breeder()
                self.manager.update_breeder(breeder,
                                            target_url=next_page_url,
                                            parse_setting_ids=breeder["parseSettingIds"],
                                            name=breeder["name"] + "下一页")
                await self.manager.add_or_update_breeder(breeder)
                # 解析新生成的爬虫（todo:之后考虑放到异步任务中）
                await self.__start_parse_by_setting(breeder)
            # 生成新爬虫完毕，若不是重复模式配置改为无下一页
            if not index_setting.get("enableNextSpiderRepeated"):
                index_setting["nextSpiderRules"] = ""
            return await self.spider_setting_proxy_client.UpdateParseSettings(index_setting)

    async def __parse_spider(self, index_setting, response, parse_setting_ids):
        if index_setting.get("parseRules") and index_setting.get("parseType") == "XPATH":
            doc = etree.HTML(response.text)
            parsed_data = doc.xpath(index_setting.get("parseRules"))
            print("parsed_data--->{}".format(parsed_data))
            # todo: 将解析完的数据存储起来
            # todo: 校验parsed_data为url
            if len(parse_setting_ids) == 1:
                return
            breeder = self.manager.create_breeder()
            self.manager.update_breeder(breeder,
                                        target_url=parsed_data,
                                        parse_setting_ids=breeder["parseSettingIds"],
                                        name=breeder["name"] + str(len(parse_setting_ids) - 1) + "子爬虫")
            await self.manager.add_or_update_breeder(breeder)
            # 解析新生成的爬虫（todo:之后考虑放到异步任务中）
            await self.__start_parse_by_setting(breeder)
