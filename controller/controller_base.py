# -*- coding: utf-8 -*-

from flask import request

from factory.manager.brand_factory import BrandManagerFactory
from factory.manager.store_factory import StoreManagerFactory
from base_cls import BaseCls


class ControllerBase(BaseCls):
    """所有支持API针对相应对象进行相关操作的Controller基类。"""

    @property
    def request(self):
        return self._request

    @property
    def user_id(self):
        return self._user_id

    @property
    def token(self):
        return self._token

    @property
    def op_func_map(self):
        return self._OP_FUNC_MAP

    @property
    def store_id(self):
        return self.get_json_param("storeId")

    @property
    def brand_id(self):
        return self.get_json_param("brandId")

    def __init__(self):
        self._request = request
        self._user_id = None
        self._brand = None
        self._store = None
        # 从request操作类型(字符串)到相应处理函数的映射。
        self._OP_FUNC_MAP = {
            "create": self.create,
            "get": self.get,
            "update": self.update,
            "list": self.list,
            "delete": self.delete
        }

    def get_header_param(self, attr, default=None):
        return self.request.headers.get(attr, default)

    def get_json_param(self, attr, default=None):
        if not self.request.is_json:
            return default
        return self.request.json.get(attr, default)

    def do_operation(self, operation):
        if not self.check_permission(operation):
            raise PermissionError('Permission denied.')
        if operation not in self.op_func_map:
            raise NotImplementedError('Operation not implemented: {}'.format(operation))
        return self.op_func_map[operation]()

    def check_permission(self, operation, request_json=None):
        return True

    def create(self):
        raise NotImplementedError("该方法未实现")

    def get(self):
        raise NotImplementedError("该方法未实现")

    def update(self):
        raise NotImplementedError("该方法未实现")

    def list(self):
        raise NotImplementedError("该方法未实现")

    def delete(self):
        raise NotImplementedError("该方法未实现")
