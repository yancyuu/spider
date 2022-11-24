# -*- coding: utf-8 -*-

from controller.controller_base import ControllerBase
from common_sdk.data_transform import protobuf_transformer
from service import errors
from manager.fixed_rules_spider_manager import FixedRulesSpiderMessageManager


class FixedRulesSpiderController(ControllerBase):
    @property
    def manager(self):
        if not self._manager:
            self._manager = FixedRulesSpiderMessageManager()
        return self._manager

    def __init__(self):
        super().__init__()
        self._OP_FUNC_MAP.update({})
        self._manager = None

    def get(self):
        fixed_rules_spider = self.manager.get_fixed_rules_spider(
            id=self.get_json_param("id"),
        )
        if not fixed_rules_spider:
            return None
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    def create(self):
        fixed_rules_spider = self.manager.create_fixed_rules_spider()
        self.manager.update_fixed_rules_spider(
            fixed_rules_spider,
            name=self.get_json_param("name"),
            spider=self.get_json_param("businessModel"),
            parse_settings=self.get_json_param("parseSettings")
        )
        self.manager.add_or_update_fixed_rules_spider(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    def delete(self):
        fixed_rules_spider = self.manager.get_fixed_rules_spider(
            id=self.get_json_param("id"),
        )
        if fixed_rules_spider is None:
            raise errors.CustomMessageError("定向爬虫不存在")
        self.manager.delete_fixed_rules_spiders(fixed_rules_spider)
        self.manager.add_or_update_fixed_rules_spider(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    def update(self):
        fixed_rules_spider = self.manager.get_fixed_rules_spider(
            id=self.get_json_param("id"),
        )
        if fixed_rules_spider is None:
            raise errors.CustomMessageError("定向爬虫不存在")
        self.manager.update(
            fixed_rules_spider,
            name=self.get_json_param("name"),
            company_id=self.get_json_param("companyId"),
            business_model=self.get_json_param("businessModel")
        )
        self.manager.add_or_update(fixed_rules_spider)
        return protobuf_transformer.protobuf_to_dict(fixed_rules_spider)

    def list(self):
        fixed_rules_spiders = self.manager.list_fixed_rules_spiders(
            status=self.get_json_param("status")
        )
        return protobuf_transformer.batch_protobuf_to_dict(fixed_rules_spiders)
