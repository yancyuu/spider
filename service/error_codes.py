# -*- coding: utf-8 -*-


SUCCESS = (0, "success")
SERVER_ERROR = (-1, "服务器错误")
PAGE_NOT_FOUND = (404, "页面未找到")
CUSTOM_MESSAGE_ERROR = (9, "{message}")

# 身份验证相关
MISSING_WX_CODE = (10001, '缺少WX_CODE参数')
MISSING_REDIRECT_URL = (10002, '缺少HREF参数')
# 要创建的实体已存在
ENTITY_EXISTS = (10003, "{type}: {name} 已存在")
