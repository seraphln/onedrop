# coding=utf8
#


"""
获取种子任务
解析页面上的url并把对应的抓取任务发送到服务器
"""

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import time
import gevent

from crawler.http import download_page
from crawler.base_crawler import BaseCrawler
from crawler.woyaogexing.parser import parse_cates

from crawler.api_proxy import get_crawler_seed


def msg_handler(seed):
    """
        检查seed，如果获取到的seed示例有问题的话，直接返回
    """
    if seed is None or seed.get("data", {}).get("seeds") is None:
        return
    else:
        try:
            seed = seed.get("data", {}).get("seeds")
            url = seed.get('url')
            target_url = url

            if_next = True
            counter = 1
            counter = 335
            target_url = "http://www.woyaogexing.com/touxiang/index_335.html"

            # 最多重试5次
            total_count = 5
            while if_next:
                print target_url
                resp = download_page(target_url)
                if not resp:
                    print "Cannot get current page: %s, Going home now!!!" % target_url
                    time.sleep(5)
                    total_counter -= 1
                    continue
                _, if_next = parse_cates(seed.get("name"), url, resp)

                total_counter = 5
                if if_next:
                    # 添加翻页
                    counter += 1
                    url_part = "index_%s.html" % counter
                    target_url = "%s%s" % (url, url_part)
        except:
            print "Seed: %s with Type: %s" % (seed, type(seed))


if __name__ == "__main__":
    task = get_crawler_seed("woyaogexing")
    msg_handler(task)
