# -*- coding: utf-8 -*-

from flask import Blueprint

from controller.fixed_rules_spider_controller import FixedRulesSpiderController
from service.base_responses import jsonify_response

bp_name = "fixed_rules_spider"
_fixed_rules_spider = Blueprint(bp_name, bp_name, url_prefix="/fixed_rules_spider")


@_fixed_rules_spider.route("/<string:operation>", methods=["POST"])
def fixed_rules_spider(operation):
    controller = FixedRulesSpiderController()
    result = controller.do_operation(operation)
    return jsonify_response(result)
