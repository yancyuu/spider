# -*- coding:utf-8 -*-

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

"""

from bs4 import BeautifulSoup

from utils.cache import cache
from utils.get_font_map import get_search_map_file
from utils.requests_utils import requests_util
from utils.logger import logger
from utils.spider_config import spider_config


class Detail():
    def __init__(self):
        self.is_ban = False

    def get_detail_font_mapping(self, shop_id):
        """
        获取detail的字体映射，不要解析，只要加密字体映射，给json用
        @param shop_id:
        @return:
        """
        url = 'http://www.dianping.com/shop/' + str(shop_id)
        r = requests_util.get_requests(url, request_type='proxy, no cookie')
        # 对于部分敏感ip（比如我的ip，淦！）可能需要带cookie才允许访问
        # request handle v2
        if r.status_code == 403:
            r = requests_util.get_requests(url, request_type='no proxy, cookie')
            if r.status_code == 403:
                logger.error('使用代理吧小伙汁')
                exit()
        text = r.text
        file_map = get_search_map_file(text)
        cache.search_font_map = file_map
        return file_map

    def get_detail(self, shop_id, request_type='proxy, cookie', last_chance=False):
        if self.is_ban and spider_config.USE_COOKIE_POOL is False:
            logger.warning('详情页请求被ban，程序继续运行')
            return_data = {
                'shop_id': shop_id,
                'shop_name': 'ban',
                'review_count': 'ban',
                'mean_price': 'ban',
                'shop_address': 'ban',
                'shop_phone_number': 'ban',
                'other_info': 'ban'
            }
            return return_data
        url = 'http://www.dianping.com/shop/' + str(shop_id)
        r = requests_util.get_requests(url, request_type=request_type)
        # 给一次retry的机会，如果依然403则判断为被ban
        if r.status_code == 403:
            if last_chance is True:
                self.is_ban = True
            return self.get_detail(shop_id=shop_id, request_type=request_type, last_chance=True)

        text = r.text
        # 获取加密文件
        file_map = get_search_map_file(text)
        # 替换加密字符串
        text = requests_util.replace_search_html(text, file_map)
        # 网页解析
        html = BeautifulSoup(text, 'lxml')
        """
        解析格式1（一般餐饮居多）
        """
        # 基础信息
        main_info = html.select('.main')[0]
        shop_name = '-'
        review_count = '-'
        shop_id_price = '-'
        address = '-'
        phone = '-'
        other_info = '-'
        try:
            base_info = main_info.select('#basic-info')[0]
            try:
                shop_name = base_info.select('.shop-name')[0].text
                # 过滤标题后缀，例：手机扫码 优惠买单
                remove_a = base_info.select('a')
                for each in remove_a:
                    shop_name = shop_name.replace(each.text, '')
                shop_name = shop_name.strip()
            except:
                shop_name = '-'
            try:
                brief_info = main_info.select('.brief-info')[0]
                try:
                    review_count = brief_info.select('#reviewCount')[0].text.strip()
                except:
                    review_count = '-'
                try:
                    shop_id_price = brief_info.select('#shop_idPriceTitle')[0].text.strip()
                except:
                    shop_id_price = '-'

                try:
                    address = main_info.find(attrs={'itemprop': 'street-address'}).text.strip()
                except:
                    address = '-'

                try:
                    phone = main_info.select('.tel')[0].text.strip()
                except:
                    phone = '-'

                try:
                    other_info = main_info.select('.other')[0].text.replace('修改', '').strip()
                except:
                    other_info = '-'
            except:
                pass
        except:
            # 切换解析方式
            pass
        """
        解析格式2（一般酒店居多）
        """
        # Todo 这种解析方式没有加密，会在解析加密文件时报错，反正这种格式数量不多，暂时不做更改了
        # if shop_name is '-':
        #     # 名称解析不到，换一种解析方式
        #     try:
        #         base_info = html.select('base-info')[0]
        #         try:
        #             shop_name = base_info.select('.hotel-title')[0].text
        #         except:
        #             shop_name = None
        #         try:
        #             address = base_info.find(attrs={'itemprop': 'address'}).text.strip()
        #         except:
        #             address = None
        #         try:
        #             score = base_info.select('.hotel-scope')[0].select('.score')[0].text
        #         except:
        #             score = None
        #     except:
        #         # Todo 前台显示手动滑动解锁
        #         # self.get_detail(shop_id)
        #         pass
        #     pass
        detail_info = {
            'shop_id': shop_id,
            'shop_name': shop_name,
            'review_count': review_count,
            'mean_price': shop_id_price,
            'shop_address': address,
            'shop_phone': phone,
            'other_info': other_info
        }
        return detail_info
