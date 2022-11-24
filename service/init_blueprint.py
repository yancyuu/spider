# -*- coding: utf-8 -*-

import time

from flask import request

from common_sdk.logging.logger import logger
from common_sdk.util import id_generator
from service.base_responses import jsonify_response
from service import error_codes, errors
from service.fixed_rules_spider_service import _fixed_rules_spider


class RequestMiddleWare:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        environ["HTTP_REQUEST_TIMESTAMP"] = time.time()
        environ["HTTP_MESSAGE_UUID"] = id_generator.generate_common_id()
        return self.wsgi_app(environ, start_response)


def init_blueprint(app):
    blueprints = [
        _fixed_rules_spider
    ]

    @app.errorhandler(404)
    def error_404(e):
        return errors.PageNotFound()

    @app.errorhandler(Exception)
    def error_handler(e):
        logger.exception(e)
        if isinstance(e, errors.Error):
            return jsonify_response(status_response=(e.errcode, e.errmsg))
        if issubclass(type(e), errors.Error):
            return jsonify_response(status_response=(e.errcode, e.errmsg))
        return jsonify_response(status_response=error_codes.SERVER_ERROR)

    @app.before_request
    def before_request():
        user_ip = request.headers.get("X-Real-Ip", None)
        if request.is_json:
            logger.info(f"{user_ip}: {request.json}")
        else:
            logger.info(f"{user_ip}")

    @app.after_request
    def response_json(response):
        """记录请求参数和返回的errcode和errmsg."""
        try:
            record_interface_cost(request, response)
        except Exception as ex:
            logger.exception(ex)
        return response

    def record_interface_cost(request, response):
        now = time.time()
        request_timestamp = request.headers.get("Request-Timestamp")
        interface_cost = now - float(request_timestamp)
        url = request.url_rule
        full_path = request.full_path
        user_ip = request.headers.get("X-Real-Ip", None)
        logger.info(f"{user_ip} 接口耗时: {interface_cost} url: {url} {full_path}")

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    app.wsgi_app = RequestMiddleWare(app.wsgi_app)
