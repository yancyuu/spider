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
from time import sleep
from webbrowser import get
from tqdm import tqdm

from function.search import Search
from function.detail import Detail
from function.review import Review
from function.get_encryption_requests import *
from utils.saver.saver import saver
from utils.spider_config import spider_config
from redis import Redis


class Controller():
    """
    整个程序的控制器
    用来进行爬取策略选择以及数据汇总存储
    """
    # 区域的映射表
    REDIS_KEY_REGOIN_MAP = "public_comment_regoin_map"
    # 上次爬到的区域
    REDIS_KEY_LAST_REGOIN_ID = "public_comment_last_regoin"
    # 分类的列表
    REDIS_KEY_CLASSFY_MAP = "public_comment_classfy_map"
    # 上次爬到的分类
    REDIS_KEY_LAST_CLASSFY_ID = "public_comment_last_classfy"
    # 页数映射
    REDIS_KEY_LAST_PAGE_MAP = "public_comment_page_map"

    def __init__(self):
        self.s = Search()
        self.d = Detail()
        self.r = Review()
        self.storage = Redis(host='127.0.0.1', port=6379)

        # 初始化基础URL
        if spider_config.SEARCH_URL == '':
            keyword = spider_config.KEYWORD
            channel_id = spider_config.CHANNEL_ID
            city_id = spider_config.LOCATION_ID
            self.base_url = 'http://www.dianping.com/search/keyword/' + str(city_id) + '/' + str(
                channel_id) + '_' + str(keyword) + '/p'
            pass
        else:
            # 末尾加一个任意字符，为了适配两种初始化url切割长度
            self.base_url = spider_config.SEARCH_URL + '1'

    def get_total_page(self, aim_url, regoin_id, class_id):
        try:
            total_page = self.storage.get(self.REDIS_KEY_LAST_PAGE_MAP+str(regoin_id)+"_"+str(class_id))
            print("dsdadsda")
            print(total_page)
            if total_page != None:
                total_page = json.loads(total_page)
            else:
                # 分析页面的page
                response = requests_util.get_requests(aim_url,'proxy, no cookie')
                if response.status_code == 403:
                    response = requests_util.get_requests(aim_url, request_type='no proxy, cookie')
                    if response.status_code == 403:
                        logger.error('使用代理吧')
                        assert "403"
                #先处理页面的数据
                each = BeautifulSoup(response.text, 'lxml')
                #获取页面的页数
                page=each.find_all('a',class_="PageLink")
                pages = [_['title'] for _ in page]
                logger.info(pages)
                total_page = int(pages[-1])
                self.storage.set(self.REDIS_KEY_LAST_PAGE_MAP+str(regoin_id)+"_"+str(class_id), total_page)
        except Exception as e:
            logger.warning("获取页数失败{url}".format(url=aim_url))
            total_page = 1
        return total_page


    '''
    获取区域的细节（为了越过50页的限制）
    '''
    def get_regoin(self):
        # 先从redis中取
        url = self.base_url + '1'
        # 从redis中取上次停止的regoin
        last_stop_regoin_id = self.storage.get(self.REDIS_KEY_LAST_REGOIN_ID)
        redis_regoin = self.storage.get(self.REDIS_KEY_REGOIN_MAP)
        redis_class = self.storage.get(self.REDIS_KEY_CLASSFY_MAP)
        last_stop_class_id = self.storage.get(self.REDIS_KEY_LAST_CLASSFY_ID)
        # 如果redis中没有就去轮询查
        if redis_regoin is None and redis_class is None:
            regoin_sub = []
            class_sub = []
            try:
                r = requests_util.get_requests(url, request_type='proxy, cookie') 
                # 对于部分敏感ip（比如我的ip，淦！）可能需要带cookie才允许访问
                # request handle v2
                print(url)
                print(r.status_code)
                if r.status_code == 403:
                    r = requests_util.get_requests(url, request_type='no proxy, cookie')
                    if r.status_code == 403:
                        logger.error('获取分类区域信息失败')
                        exit()
                text = r.text 
                # 网页解析
                html = BeautifulSoup(text, 'lxml')
                # 频道信息
                try:
                    navigation_info = html.select('.navigation')[0]    
                    print(navigation_info) 
                    try:
                        # 获取分类
                        catoray_info = navigation_info.select("#classfy")[0]
                        # 获取所有的a标签
                        all = catoray_info.find_all('a')
                        for _ in all:
                            class_sub.append(_['data-cat-id'])
                        # 获取分类
                        catoray_info = navigation_info.select("#classfy")[0]
                        # 获取所有的a标签
                        all = catoray_info.find_all('a')
                        for _ in all:
                            class_sub.append(_['data-cat-id'])
                        # 获取区域信息
                        regoin_info = navigation_info.select("#bussi-nav")[0]
                        # 获取所有的a标签
                        all = regoin_info.find_all('a')
                        for _ in all:
                            regoin_sub.append(_['data-cat-id'])
                        self.storage.set(self.REDIS_KEY_REGOIN_MAP,json.dumps(regoin_sub))
                        self.storage.set(self.REDIS_KEY_CLASSFY_MAP,json.dumps(class_sub))
                    except:
                        logger.error('获取分类信息失败')
                except:
                    navigation_info = '-'
            except Exception as e:
                print(e)
        else:
            regoin_sub = json.loads(redis_regoin)
            class_sub = json.loads(redis_class)
        # 过滤掉上次已经查过的regoin
        if regoin_sub != [] and last_stop_regoin_id is not None:
            last_stop_regoin_id = json.loads(last_stop_regoin_id)
            for index in range(1,len(regoin_sub)):
                sub_id,sub_name = regoin_sub[index]
                if int(last_stop_regoin_id) == int(sub_id):
                    return regoin_sub[index:]
        
        # 过滤掉上次已经查过的分类
        if class_sub != [] and last_stop_class_id is not None:
            last_stop_class_id = json.loads(last_stop_class_id)
            for index in range(1,len(class_sub)):
                sub_id,sub_name = class_sub[index]
                if int(last_stop_class_id) == int(sub_id):
                    return class_sub[index:]
        return regoin_sub,class_sub

    def main(self,pages=spider_config.NEED_SEARCH_PAGES, start_page = 1, url=""):
        """
        调度
        @return:
        """
        # Todo  其实这里挺犹豫是爬取完搜索直接详情还是爬一段详情一段
        #       本着稀释同类型访问频率的原则，暂时采用爬一段详情一段
        # 调用搜索
        for page in tqdm(range(start_page, pages + 1), desc='搜索页数'):
            # 拼凑url
            if url != "":
                search_url, request_type = url+'p{p}'.format(p=page),'proxy,no cookie'
            else:
                search_url, request_type = self.get_search_url(page)
            print(search_url)
            """
            {
                '店铺id': -,
                '店铺名': -,
                '评论总数': -,
                '人均价格': -,
                '标签1': -,
                '标签2': -,
                '店铺地址': -,
                '详情链接': -,
                '图片链接': -,
                '店铺均分': -,
                '推荐菜': -,
                '店铺总分': -,
            }
            """
            search_res = self.s.search(search_url, request_type)

            if spider_config.NEED_DETAIL is False and spider_config.NEED_REVIEW is False:
                for each_search_res in search_res:
                    each_search_res.update({
                        'shop_phone': '-',
                        'other_info': '-',
                        'coupon_info': '-',
                    })
                    self.saver(each_search_res, {})
                continue
            for each_search_res in tqdm(search_res, desc='详细爬取'):
                each_detail_res = {}
                each_review_res = {}
                # 爬取详情
                if spider_config.NEED_DETAIL:
                    shop_id = each_search_res['shop_id']
                    if spider_config.NEED_PHONE_DETAIL:
                        """
                        {
                            '店铺id': -,
                            '店铺名': -,
                            '评论总数': -,
                            '人均价格': -,
                            '店铺地址': -,
                            '店铺电话': -,
                            '其他信息': -
                        }
                        """
                        each_detail_res = self.d.get_detail(shop_id)
                        # 多版本爬取格式适配
                        each_detail_res.update({
                            'star_point': '-',
                            'comment_list': '-',
                            'coupon_info': '-',
                        })
                    else:
                        """
                        {
                            '店铺id': -,
                            '店铺名': -,
                            '店铺地址': -,
                            '店铺电话': -,
                            '店铺总分': -,
                            '店铺均分': -,
                            '人均价格': -,
                            '评论总数': -,
                        }
                        """
                        hidden_info = get_basic_hidden_info(shop_id)
                        review_and_star = get_review_and_star(shop_id)
                        each_detail_res.update(hidden_info)
                        each_detail_res.update(review_and_star)
                        # 多版本爬取格式适配
                        each_detail_res.update({
                            'other_info': '-',
                            'coupon_info': '-'
                        })
                    # 全局整合，将详情以及评论的相关信息拼接到search_res中。
                    each_search_res['shop_address'] = each_detail_res['shop_address']
                    each_search_res['shop_phone'] = each_detail_res['shop_phone']
                    each_search_res['star_point'] = each_detail_res['star_point']
                    if each_search_res['comment_list'] == '-':
                        each_search_res['comment_list'] = each_detail_res['comment_list']
                    each_search_res['mean_price'] = each_detail_res['mean_price']
                    each_search_res['review_count'] = each_detail_res['review_count']
                    each_search_res['other_info'] = each_detail_res['other_info']
                    each_search_res['coupon_info'] = each_detail_res['coupon_info']
                # 爬取评论
                if spider_config.NEED_REVIEW:
                    shop_id = each_search_res['shop_id']
                    if spider_config.NEED_REVIEW_DETAIL:
                        """
                        {
                            'shop_id': -,
                            'summaries': -,
                            'review_number': -,
                            'good_review_count': -,
                            'mid_review_count': -,
                            'bad_review_count': -,
                            'review_with_pic_count': -,
                            'all_review': -,
                        }
                        """
                        each_review_res = self.r.get_review(shop_id)
                        each_review_res.update({'recommend': '-'})
                    else:
                        """
                        {
                            '店铺id': -,
                            'summaries': -,
                            '评论总数': -,
                            'good_review_count': -,
                            'mid_review_count': -,
                            'bad_review_count': -,
                            'review_with_pic_count': -,
                            'all_review': -,
                            '推荐菜': -,
                        }
                        """
                        each_review_res = get_basic_review(shop_id)

                        # 全局整合，将详情以及评论的相关信息拼接到search_res中。
                        each_search_res['recommend'] = each_review_res['recommend']
                        # 对于已经给到search_res中的信息，删除
                        each_review_res.pop('recommend')

                self.saver(each_search_res, each_review_res)

    def get_review(self, shop_id, detail=False):
        if detail:
            each_review_res = self.r.get_review(shop_id)
        else:
            each_review_res = get_basic_review(shop_id)
        saver.save_data(each_review_res, 'review')

    def get_detail(self, shop_id, detail=False):
        each_detail_res = {}
        if detail:
            each_detail_res = self.d.get_detail(shop_id)
            # 多版本爬取格式适配
            each_detail_res.update({
                'star_point': '-',
                'shop_point': '-',
            })
        else:
            hidden_info = get_basic_hidden_info(shop_id)
            review_and_star = get_review_and_star(shop_id)
            each_detail_res.update(hidden_info)
            each_detail_res.update(review_and_star)
            # 多版本爬取格式适配
            each_detail_res.update({
                'other_info': '-'
            })
        saver.save_data(each_detail_res, 'detail')

    def get_search_url(self, cur_page):
        """
        获取搜索链接
        @param cur_page:
        @return:
        """
        if cur_page == 1:
            # return self.base_url[:-2], 'no proxy, no cookie'
            return self.base_url[:-2], 'proxy, cookie'
        else:
            if self.base_url.endswith('p'):
                return self.base_url + str(cur_page), 'proxy, cookie'
            else:
                return self.base_url[:-1] + str(cur_page), 'proxy, cookie'

    def saver(self, each_search_res, each_review_res):
        # save search
        saver.save_data(each_search_res, 'search')
        # save detail
        # if spider_config.NEED_DETAIL:
        #     saver.save_data(each_detail_res, 'detail')

        # save review
        if spider_config.NEED_REVIEW:
            saver.save_data(each_review_res, 'review')


controller = Controller()
