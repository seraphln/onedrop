# coding=utf8
#


"""
xindebaby 医院详细页面的采集程序

目前只提供医院信息的采集
"""

from gevent import monkey
monkey.patch_all()

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import gevent

from crawler.http import download_page
from crawler.base_crawler import BaseCrawler
from crawler.api_proxy import get_crawler_task

from crawler.xindebaby.parser import parse_detail_page


class XindeBabyTaskCrawler(BaseCrawler):
    """ baike.pcbaby.com.cn对应的爬虫实现 """

    def get_task(self):
        """ 从远程服务器获取pcbaby的爬虫种子 """
        return get_crawler_task(self.source)


def msg_handler(task):
    """
    检查seed，如果获取到的seed示例有问题的话
    就直接返回
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

    xindebaby = XindeBabyTaskCrawler(callback=msg_handler,
                                     ttype="page",
                                     source="xindebaby")
    xindebaby.start()
    gevent.wait()
    #task = get_crawler_task("xindebaby")
    #msg_handler(task)
