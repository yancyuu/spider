# -*- coding: utf-8 -*-

from fastapi import APIRouter, Request

from controller.fixed_rules_spider_controller import FixedRulesSpiderController
from service.base_responses import jsonify_response

bp_name = "fixed_rules_spider"
_fixed_rules_spider = APIRouter(prefix="/fixed_rules_spider",
                                tags=["固定规则爬虫"],
                                responses={404: {"description": "Not found"}})


@_fixed_rules_spider.post("/{operation}")
async def fixed_rules_spider(req: Request, operation: str):
    controller = FixedRulesSpiderController(req)
    result = await controller.do_operation(operation)
    return jsonify_response(result)
