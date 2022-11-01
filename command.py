# -*- coding:utf-8 -*-
# Desc: 用来命令行调度（用来测试）
"""
      ┏┛ ┻━━━━━┛ ┻┓
      ┃　　　　　　 ┃
      ┃　　　━　　　┃
      ┃　┳┛　  ┗┳　┃
      ┃　　　　　　 ┃
      ┃　　　┻　　　┃
      ┃　　　　　　 ┃
      ┗━┓　　　┏━━━┛
        ┃　　　┃   神兽保佑
        ┃　　　┃   代码无BUG！
        ┃　　　┗━━━━━━━━━┓
        ┃CREATE BY SNIPER┣┓
        ┃　　　　         ┏┛
        ┗━┓ ┓ ┏━━━┳ ┓ ┏━┛
          ┃ ┫ ┫   ┃ ┫ ┫
          ┗━┻━┛   ┗━┻━┛
测试运行:
跑详细信息
python3 command.py --normal 0 --detail 2 --need_more True
python3 command.py --normal 0 --detail 2 --need_more False
跑基本信息
python3 command.py --normal 2
"""

import argparse
from utils.spider_controller import controller
from utils.logger import logger
from concurrent.futures import ThreadPoolExecutor
from utils.cache import cache,Cache
from utils.database_utils import DataBaseUtils
import json

parser = argparse.ArgumentParser()

parser.add_argument('--normal', type=int, required=False, default=0,
                    help='spider as normal(search->detail->review)')
parser.add_argument('--detail', type=int, required=False, default=0,
                    help='spider as custom(just detail)')
parser.add_argument('--review', type=int, required=False, default=0,
                    help='spider as custom(just review)')
parser.add_argument('--shop_id', type=str, required=False, default='',
                    help='custom shop id')
parser.add_argument('--need_more', type=bool, required=False, default=False,
                    help='need detail')
parser.add_argument('--start_page', type=int, required=False, default=1,
                    help='need start_page')
args = parser.parse_args()
if __name__ == '__main__':
    false_basic_msg = []
    if args.normal == 1:
        controller.main()
    #测试用
    if args.normal == 2:
        area = controller.get_regoin()
        url = "http://www.dianping.com/search/keyword/7/10_深圳"
        # 获取区域值
        regions = area[0]
        # 获取详细分类
        classfy = area[1]
        # 开启多线程
        thread_pool = ThreadPoolExecutor(max_workers=2)
        for sub_class in classfy:
            # controller.main(total_page, args.start_page, aim_url)
            #捕捉运行时的异常
            thread_pool.submit(lambda p: controller.captcher_except(*p), [url,sub_class]) 
        thread_pool.shutdown(wait= True)

    if args.detail == 1:
        shop_id = args.shop_id
        logger.info('爬取shop_id：' + shop_id + '详情')
        controller.get_detail(shop_id, detail=args.need_more)
    
    #Todo :更新已经查找过基本信息的店铺
    if args.detail == 2:
        # 开启多线程
        thread_pool = ThreadPoolExecutor(max_workers=3)
        page = 0
        while True:
            page += 1
            # 分页查找
            data = DataBaseUtils().get_search_list(page, 10) 
            if data == []:
                break
            for _ in data:
                shop_id = _['shop_id']
                detail_cache = cache.cache.hget(Cache.REDIS_KEY_CRAWL_DETAIL, shop_id)
                if detail_cache is not None:
                    continue
                logger.info('爬取shop_id：' + shop_id + '详情')
                thread_pool.submit(lambda p: controller.get_detail(*p), [shop_id, args.need_more])
                break
            break
        thread_pool.shutdown(wait= True)
            

    if args.review == 1:
        shop_id = args.shop_id
        logger.info('爬取shop_id：' + shop_id + '评论')
        controller.get_review(shop_id, detail=args.need_more)
