# -*- coding: utf-8 -*-

from common_sdk.logging.logger import logger
from service.base_responses import jsonify_response
from service import error_codes, errors
from service.fixed_rules_spider_service import _fixed_rules_spider
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from common_sdk.util import context
from common_sdk.util import id_generator
import time


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        context.set_message_uuid(id_generator.generate_common_id())
        context.set_request_timestamp(int(time.time()))
        response = await call_next(request)
        """记录请求参数和返回的errcode和errmsg."""
        try:
            self.record_interface_cost(request, response)
        except Exception as ex:
            logger.exception(ex)
        return response

    @staticmethod
    def record_interface_cost(request, response):
        now = time.time()
        request_timestamp = context.get_request_timestamp()
        interface_cost = now - float(request_timestamp)
        url = request.url

        full_path = request.path_params
        user_ip = request.headers.get("X-Real-Ip", None)
        logger.info(f"{user_ip} 接口耗时: {interface_cost} url: {url} {full_path}")


def init_blueprint(app):
    blueprints = [
        _fixed_rules_spider
    ]

    @app.exception_handler(404)
    def error_404(request: Request, exc: 404):
        return jsonify_response(status_response=error_codes.PAGE_NOT_FOUND)

    @app.exception_handler(Exception)
    def error_handler(request: Request, exc: Exception):
        logger.exception(exc)
        if isinstance(exc, errors.Error):
            return jsonify_response(status_response=(exc.errcode, exc.errmsg))
        if issubclass(type(exc), errors.Error):
            return jsonify_response(status_response=(exc.errcode, exc.errmsg))
        return jsonify_response(status_response=error_codes.SERVER_ERROR)

    for blueprint in blueprints:
        app.include_router(blueprint)

    app.add_middleware(RequestContextMiddleware)
