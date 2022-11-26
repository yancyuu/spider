from common_sdk.system.sys_env import get_env
from common_sdk.base_class.singleton import SingletonMetaThreadSafe
from spider_sdk.client.actor_proxy_client import ActorProxyClient

'''
用来调度异步任务
'''


class InitTask(metaclass=SingletonMetaThreadSafe):

    @staticmethod
    async def proxy_task():
        actor_client = ActorProxyClient("proxy_task")
        if get_env("USE_PROXY_POOL"):
            # Create proxy client
            actor_proxy = actor_client.create_proxy_actor_proxy()
            # 开始生产proxy
            await actor_proxy.GetMyData()

    @staticmethod
    async def cookie_task():
        actor_client = ActorProxyClient("cookie_task")
        if get_env("USE_COOKIE_POOL"):
            # Create proxy client
            actor_proxy = actor_client.create_cookie_actor_proxy()
            # 开始生产cookie
            await actor_proxy.GetMyData()
