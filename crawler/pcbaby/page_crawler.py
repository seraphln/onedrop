# coding=utf8
#


"""
太平洋亲子网的爬虫实现

目前将爬虫分为如下几个部分：
1. 导航栏的采集，包括：怀孕、育儿、营养、生活、用品、生男生女、食谱、用品常识
2. 二级导航，包括：孕育周刊、母婴检查、疾病防疫、营养饮食、保健护理
3. 三级导航，包括: 备孕百科及子分类等
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

from crawler.pcbaby.parser import parse_detail_page


class PCBabyTaskCrawler(BaseCrawler):
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
        print "No more seed! Going home now!!!"
        return
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


if __name__ == "__main__":
    pcbaby = PCBabyTaskCrawler(callback=msg_handler,
                               ttype="page",
                               source="pcbaby")
    pcbaby.start()
    gevent.wait()
