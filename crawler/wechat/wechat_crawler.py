# coding=utf8
#


"""
微信数据采集插件的主文件。
代码执行流程如下：
    python crawler.py --name=<公众号名称>
"""

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import lxml.etree
import json
import time
import argparse
import requests
import xmltodict

import urllib
from urllib2 import urlparse

from http import get_proxy
from http import default_headers
from utils import generate_proxy

from http import download_page

from parser import parse_user_info
from parser import find_correct_element_url


start_flag = None

base_url = "https://weixin.sogou.com/"
base_css_url = 'https://www.sogou.com/sug/css/m3.min.v.2.css?v=1'
base_pb_url = 'https://pb.sogou.com/pb.js'


search_url = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=y&_sug_type_="

DEFAULT_TIMEOUT = 3


def update_headers(headers, host, referer):
    """ 更新header信息 """

    headers.update({"Host": host,
                    "Referer": referer})


def parse_options():
    """
    解析输入
    """
    parser = argparse.ArgumentParser(description='compare market and site number')
    parser.add_argument('-n', '--name', action='store', dest='name',
                        help=u'需要搜索的微信公众号名称')

    return parser.parse_args()


def download_content_list(content_lst, headers, timeout):
    """
        通过给定的content_url来打开具体的url页面，并采集相关信息
    """
    import ipdb;ipdb.set_trace()
    for content in content_lst:
        c = content["app_msg_ext_info"]
        target_url = c["content_url"]
        print target_url
        resp = download_page(target_url, headers, timeout=timeout)

    #global start_flag
    #total_records = 0
    #context_lst = []
    #_t = start_flag
    #now = int(time.time() * 1000)
    #url_netloc = urlparse.urlsplit(detail_url)
    #cur_url = 'http://%s/gzhjs?%s' % (url_netloc.netloc, url_netloc.query)
    #params = "cb=sogou.weixin_gzhcb&page=%s&gzhArtKeyWord=&tsn=0&t=%s&_=%s"
    #query_url = cur_url + '&' + params

    #for i in range(1, 11):
    #    target_url = query_url % (i, now, _t)
    #    print target_url
    #    resp = download_page(target_url, headers, timeout=DEFAULT_TIMEOUT)
    #    strip_text = resp.text.replace('sogou.weixin_gzhcb(', '')
    #    strip_text = strip_text[:len(strip_text)-1]
    #    context_lst.extend(json.loads(strip_text).get('items', []))
    #    if not total_records:
    #        total_records = json.loads(strip_text).get('totalItems', 0)
    #    _t = _t + 1
    #    time.sleep(2)

    #return context_lst


def main(params):
    """
    1. 解析采集的公众号
    2. 读取代理ip列表
    3. 采集具体的公众号信息
    4. 下载内容并保存到数据文件
    """

    # start_flag as a js timestamp
    global start_flag
    global search_url

    headers = default_headers()

    #while 1:
    # open the base page
    download_page(base_url, headers, timeout=DEFAULT_TIMEOUT)

    # download a css url
    download_page(base_css_url, headers, timeout=DEFAULT_TIMEOUT)

    # download a js
    download_page(base_pb_url, headers, timeout=DEFAULT_TIMEOUT)
    ## finished the base cookie download

    start_flag = start_flag or int(time.time() * 1000)
    search_url = search_url % urllib.quote(params.name)
    search_resp = download_page(search_url, timeout=DEFAULT_TIMEOUT)

    el = lxml.etree.HTML(search_resp.text)
    detail_url = find_correct_element_url(params, el, search_resp)
    # parse the search_resp and get the correct info

    if detail_url:
        detail_resp = download_page(detail_url, headers, timeout=DEFAULT_TIMEOUT)
        el = lxml.etree.HTML(detail_resp.text)

        user_info, content_lst = parse_user_info(el, detail_resp.text)

        import ipdb;ipdb.set_trace()
        headers = update_headers(headers, "mp.weixin.com.cn", detail_url)
        content_lst = download_content_list(content_lst, headers, timeout=DEFAULT_TIMEOUT)
        for cur_content in content_lst:
            data = cur_content.replace('encoding="gbk"', 'encoding="utf-8"')
            data = json.loads(json.dumps(xmltodict.parse(data)))
            content_url = '%s%s' % ('http://weixin.sogou.com/', data.get('DOCUMENT').get('item').get('display').get('url'))
            resp = download_page(content_url, headers, timeout=DEFAULT_TIMEOUT)
        print 'foo'
    else:
        print u"无法找到对应的公众号，请检查是否输入错信息"


if __name__ == '__main__':
    params = parse_options()
    main(params)
