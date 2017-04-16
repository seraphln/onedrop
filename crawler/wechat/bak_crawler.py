# coding=utf8
#


"""
微信数据采集插件的主文件。
代码执行流程如下：
    python crawler.py --name=<公众号名称>
"""


import lxml.etree
import json
import time
import random
import argparse
import requests
import xmltodict
from datetime import datetime

import urllib
from urllib2 import urlparse

from http import get_proxy
from http import default_headers
from utils import generate_proxy


proxies = get_proxy()

base_url = "http://weixin.sogou.com/"

WITH_PROXY = 1
DEFAULT_TIMEOUT = 1


def parse_options():
    """
    解析输入
    """
    parser = argparse.ArgumentParser(description='compare market and site number')
    parser.add_argument('-n', '--name', action='store', dest='name',
                        help=u'需要搜索的微信公众号名称')

    return parser.parse_args()


def download_page(url, headers, _cookie, timeout, proxy_dict=None):
    """
    """
    query_dict = {'url': url, 'headers': headers,
                  'timeout': timeout, 'proxies': proxy_dict}

    while 1:
        try:
            if _cookie:
                query_dict['cookies'] = _cookie
            resp = requests.get(**query_dict)
            if resp.text:
                break
        except Exception as e:
            if 'timeout' in str(e):
                return 'timeout'
            if 'Connection aborted.' in str(e):
                time.sleep(1)

            import traceback
            print traceback.print_exc()
            return ''

    return resp


def open_base_page(base_url, _cookie, headers, proxies):
    """ """
    proxy_dict = {}
    meta_info = ()
    query_dict = {'url': base_url, 'headers': headers, '_cookie': _cookie, 'timeout': DEFAULT_TIMEOUT}
    if WITH_PROXY:
        proxy_dict, meta_info = generate_proxy(proxies)
        query_dict['proxy_dict'] = proxy_dict
    while 1:
        resp = download_page(**query_dict)
        if resp == 'timeout' or not resp:
            if WITH_PROXY:
                host, port, http_method = meta_info
                print host, port, http_method
                proxies.remove([host, port, http_method])
                if not proxies:
                    proxies = get_proxy(if_force=True)
                proxy_dict, meta_info = generate_proxy(proxies)
            else:
                break
        else:
            _cookie = resp.cookies
            break

    print _cookie.items()
    return proxy_dict, _cookie, resp, meta_info


def download_search_page(search_url, _cookie, headers, proxy_dict, proxies, meta_info):
    """ """
    query_dict = {'url': search_url, 'headers': headers,
                  '_cookie': _cookie, 'timeout': DEFAULT_TIMEOUT}
    while 1:
        if WITH_PROXY:
            query_dict['proxy_dict'] = proxy_dict
        resp = download_page(**query_dict)
        if resp == 'timeout' or not resp:
            if WITH_PROXY:
                host, port, http_method = meta_info
                print host, port, http_method
                proxies.remove([host, port, http_method])
                if not proxies:
                    proxies = get_proxy(if_force=True)
                proxy_dict, meta_info = generate_proxy(proxies)
            else:
                break
        else:
            _cookie = resp.cookies
            break

    print _cookie.items()
    return proxy_dict, _cookie, resp, meta_info


def download_detail_list_by_page(detail_url, _cookie, headers, proxy_dict, proxies, meta_info):
    """ """
    query_dict = {'url': detail_url, 'headers': headers,
                  '_cookie': _cookie, 'timeout': DEFAULT_TIMEOUT}
    while 1:
        if WITH_PROXY:
            query_dict['proxy_dict'] = proxy_dict
        resp = download_page(**query_dict)
        if resp == 'timeout' or not resp:
            if WITH_PROXY:
                host, port, http_method = meta_info
                print host, port, http_method
                proxies.remove([host, port, http_method])
                if not proxies:
                    proxies = get_proxy(if_force=True)
                proxy_dict, meta_info = generate_proxy(proxies)
            else:
                break
        else:
            _cookie = resp.cookies
            break

    el = lxml.etree.HTML(resp.text)
    user_info = parse_user_info(el)

    return user_info, _cookie


def parse_user_info(el):
    """

    """
    user_info = {}
    user_el = el.xpath('//div[@id="sogou_vr__box_0"]')[0]
    user_img = user_el.xpath('./div[@class="img-box"]/a/img/@src')[0]
    user_name = user_el.xpath('./div[@class="txt-box"]/h3[@id="weixinname"]/text()')[0]
    user_wechatid = user_el.xpath('./div[@class="txt-box"]/h4/span/label[@name="em_weixinhao"]/text()')[0]
    user_desc = user_el.xpath('./div[@class="txt-box"]/div[@class="s-p2"]')[0].xpath('./span[@class="sp-txt"]/text()')[0]
    user_verify_info = user_el.xpath('./div[@class="txt-box"]/div[@class="s-p2"]')[1].xpath('./span[@class="sp-txt"]/text()')[0]
    user_gram = user_el.xpath('./div[@class="v-box"]/img/@src')[0]

    return {'user_img': user_img, 'username': user_name,
            'user_wechatid': user_wechatid,
            'user_desc': user_desc,
            'user_verify_info': user_verify_info,
            'user_gram_link': user_gram}


def find_correct_element_url(params, el):
    els = el.xpath('//div[@class="wx-rb bg-blue wx-rb_v1 _item"]')
    print '---------------------------'
    print len(els)
    print '---------------------------'
    for cur_el in els:
        nick_name = cur_el.xpath('//div[@class="txt-box"]/h3/em/text()')[0]
        print nick_name
        if params.name == nick_name.encode('utf8'):
            url = cur_el.xpath('@href')[0]
            url = urlparse.urljoin(base_url, url)
            return url

    return ""


def download_content_list(detail_url, _cookie, headers,
                          proxy_dict, proxies, meta_info):
    """
    sample url: http://weixin.sogou.com/gzhjs?openid=oIWsFt86NKeSGd_BQKp1GcDkYpv0&ext=D4y5Z3wUwj5uk6W7Yk9BqC3LAaFqirWHT5QFje14y0dip_leVhZF6qjo9Mm_UUVg&cb=sogou.weixin_gzhcb&page=1&gzhArtKeyWord=&tsn=0&t=1459425446419&_=1459425446169

    其中openid是固定的
    ext也是固定的
    cb=sogou.weixin_gzhcb这个也是固定的
    唯一变化的就是这个t以及_这2个字段，看上去是打开这个页面的时间戳
    """
    total_records = 0
    context_lst = []
    _t = int(time.time() * 1000)
    now = int(time.time() * 1000)
    url_netloc = urlparse.urlsplit(detail_url)
    cur_url = 'http://%s/gzhjs?%s' % (url_netloc.netloc, url_netloc.query)
    params = "cb=sogou.weixin_gzhcb&page=%s&gzhArtKeyWord=&tsn=0&t=%s&_=%s"
    query_url = cur_url + '&' + params

    for i in range(1, 11):
        target_url = query_url % (i, now, _t)
        resp = requests.get(target_url, cookies=_cookie,
                            headers=headers, timeout=DEFAULT_TIMEOUT, proxies=proxy_dict)
        strip_text = resp.text.replace('sogou.weixin_gzhcb(', '')
        strip_text = strip_text[:len(strip_text)-1]
        context_lst.extend(json.loads(strip_text).get('items', []))
        if not total_records:
            total_records = json.loads(strip_text).get('totalItems', 0)
        _t = _t + 1
        time.sleep(2)
        cur_content = context_lst[0]
        data = cur_content.replace('encoding="gbk"', 'encoding="utf-8"')
        data = json.loads(json.dumps(xmltodict.parse(data)))
        content_url = '%s%s' % ('http://weixin.sogou.com/', data.get('DOCUMENT').get('item').get('display').get('url'))
        resp = download_page(content_url, headers, _cookie, timeout=DEFAULT_TIMEOUT)
        _cookie = resp.cookies

    return context_lst, _cookie


def main(params):
    """
    1. 解析采集的公众号
    2. 读取代理ip列表
    3. 采集具体的公众号信息
    4. 下载内容并保存到数据文件
    """
    global proxies
    if not proxies:
        proxies = get_proxy(if_force=True)

    _cookie = None
    headers = default_headers()

    #while 1:
    # open the base page
    proxy_dict, _cookie, resp, meta_info = open_base_page(base_url, _cookie, headers, proxies)
    search_url = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=y&_sug_type_=" % urllib.quote(params.name)
    proxy_dict, _cookie, search_resp, meta_info = download_search_page(search_url, _cookie,
                                                                       headers, proxy_dict, proxies, meta_info)
    el = lxml.etree.HTML(search_resp.text)
    detail_url = find_correct_element_url(params, el)
    # parse the search_resp and get the correct info

    if detail_url:
        user_info, _cookie = download_detail_list_by_page(detail_url, _cookie,
                                                          headers, proxy_dict, proxies, meta_info)
        print _cookie
        content_lst, _cookie = download_content_list(detail_url, _cookie, headers,
                                                     proxy_dict, proxies, meta_info)
        print _cookie
        for cur_content in content_lst:
            data = cur_content.replace('encoding="gbk"', 'encoding="utf-8"')
            data = json.loads(json.dumps(xmltodict.parse(data)))
            content_url = '%s%s' % ('http://weixin.sogou.com/', data.get('DOCUMENT').get('item').get('display').get('url'))
            resp = download_page(content_url, headers, _cookie, timeout=DEFAULT_TIMEOUT)
        print 'foo'
    else:
        print u"无法找到对应的公众号，请检查是否输入错信息"
        proxies = get_proxy(if_force=True)


if __name__ == '__main__':
    params = parse_options()
    main(params)
