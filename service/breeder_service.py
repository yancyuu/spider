# -*- coding: utf-8 -*-

from fastapi import APIRouter, Request

from controller.breeder_controller import BreederController
from service.base_responses import jsonify_response

bp_name = "breeder"
_breeder = APIRouter(prefix="/breeder",
                     tags=["爬虫母体"],
                     responses={404: {"description": "Not found"}})


@_breeder.post("/{operation}")
async def breeder(req: Request, operation: str):
    controller = BreederController(req)
    result = await controller.do_operation(operation)
    return jsonify_response(result)
