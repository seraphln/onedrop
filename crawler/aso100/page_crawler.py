# coding=utf8
#


"""
huabian.com的爬虫实现
"""

from gevent import monkey
monkey.patch_all()

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import gevent

import json
from crawler.http import download_page

from crawler.base_crawler import BaseCrawler

from crawler.api_proxy import get_crawler_task

from crawler.huabian.parser import parse_detail_page

from crawler.aso100.seed_crawler import get_proxy_browser


class ASO100TaskCrawler(BaseCrawler):
    """ aso100详细页面对应的爬虫实现 """

    def get_task(self):
        """ 从远程服务器获取aso100的爬虫种子 """
        return get_crawler_task(self.source)


def crawler_page(appid):
    """
        具体执行的采集页面详细信息的实现

        @param appid: 需要采集的appid
        @type appid: String
    
        :return:
    """
    #browser = get_proxy_browser()

    browser = webdriver.Firefox()

    keyword_lst = ["baseinfo",      # 基本信息
                   "version",       # 版本信息
                   "rank",          # 实时排名
                   "globalRank",    # 全球统一排名
                   "keyword",       # 关键词明细
                   "rankMonitor",   # 关键词监控
                   "keywordGuide",  # 关键词优化工具
                   "competi",       # 竞品概况
                   "rankCompare",   # 排名对比
                   "asoCompare",    # ASO对比
                   "comment",       # 评论统计
                   "commentList",   # 评论详情]

    for keyword in keyword_lst:
        




def msg_handler(task):
    """
    检查task，如果获取到的task实例有问题的话
    就直接返回
    {'data': {'tasks': None}}
    """
    if task is None or task.get("data", {}).get("tasks") is None:
        return False
    else:
        try:
            task = task.get("data", {}).get("tasks")
            url = task.get('url')
            if not url.startswith("http:"):
                url = "http:" + url
            print "Going to crawl url: ", url
            resp = download_page(url, not_proxy=True)
            if not resp:
                print "Cannot get current page: %s, sleeping now!!!" % url
            content, task = parse_detail_page(resp.text, task)
            with open("result.txt", "a+") as fp:
                task["title"] = task.get("title")
                fp.write("%s\n" % json.dumps(task))
        except:
            print "Task: %s with Type: %s" % (task, type(task))

    return True


if __name__ == "__main__":
    #pcbaby = PCBabyTaskCrawler(callback=msg_handler,
    #                           ttype="page",
    #                           source="pcbaby")
    #pcbaby.start()
    #gevent.wait()
    data = json.load(open("seeds.txt"))
    for cur_task in data:
        url = cur_task.get("url")
        seed = {"data": {"tasks": {"url": url, "name": "mingxing", "title": cur_task.get("title")}}}
        print msg_handler(seed)
