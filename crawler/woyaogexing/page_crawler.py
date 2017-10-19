# coding=utf8
#


"""
获取具体的任务
解析页面，并把结果上传到远程服务器
"""

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import time
import gevent

from crawler.http import download_page
from crawler.base_crawler import BaseCrawler
from crawler.woyaogexing.parser import parse_detail_page

from crawler.api_proxy import get_crawler_task


class WoYaoGeXingTaskCrawler(BaseCrawler):
    """ baike.pcbaby.com.cn对应的爬虫实现 """

    def get_task(self):
        """ 从远程服务器获取pcbaby的爬虫种子 """
        return get_crawler_task(self.source)


def msg_handler(task):
    """
        检查任务，如果获取到的task信息有问题的话，直接返回
        这里需要解析页面中具体的图片链接，需要下载图片到本地
        并上传到线上服务器
        {'data': {'tasks': None}}
    """
    if task is None or task.get("data", {}).get("tasks") is None:
        return False
    else:
        try:
            task = task.get("data", {}).get("tasks")
            url = task.get('url')
            print "Going to crawl url: ", url
            resp = download_page(url, not_proxy=True)
            if not resp:
                print "Cannot get current page: %s, sleeping now!!!" % url
            parse_detail_page(resp.text, task)
        except:
            print "Task: %s with Type: %s" % (task, type(task))

    return True


if __name__ == "__main__":
    #task = get_crawler_task("woyaogexing")
    #msg_handler(task)
    gexing_crawler = WoYaoGeXingTaskCrawler(callback=msg_handler,
                                            ttype="page",
                                            source="woyaogexing")
    gexing_crawler.start()
    gevent.wait()
