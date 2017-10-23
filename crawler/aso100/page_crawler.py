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

import json
import lxml
from selenium import webdriver
from crawler.http import download_page
from crawler.base_crawler import BaseSeleniumCrawler

from crawler.base_crawler import BaseCrawler

from crawler.api_proxy import get_crawler_task

from crawler.aso100.parser import process_base_info
from crawler.aso100.parser import process_version_info
from crawler.aso100.parser import process_compete_info
from crawler.aso100.parser import process_comment_info

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

    base_url = "https://aso100.com/app/%s/appid/1044283059/country/cn"
    browser = webdriver.Firefox()

    keyword_mapper = {#"baseinfo": process_base_info,               # 基本信息
                      #"version": process_version_info,             # 版本信息
                      #"rank": process_rank_info,                   # 实时排名
                      #"globalRank": process_global_rank_info,      # 全球统一排名
                      #"keyword": process_keyword_info,             # 关键词明细
                      #"rankMonitor": process_rank_monitor_info,    # 关键词监控
                      #"keywordGuide": process_keyword_guide,       # 关键词优化工具
                      #"competi": process_compete_info,             # 竞品概况
                      #"rankCompare": process_rank_compare_info,    # 排名对比
                      #"asoCompare": process_aso_compare_info,      # ASO对比
                      "comment": process_comment_info,             # 评论统计
                      #"commentList": process_comment_list_info,    # 评论详情
            }

    info_dict = {}
    for keyword, task in keyword_mapper.iteritems():
        url = base_url % keyword
        browser.get(url)
        el = lxml.etree.HTML(browser.page_source)
        task(el, info_dict)
        print info_dict

    return info_dict


#def msg_handler(task):
#    """
#    检查task，如果获取到的task实例有问题的话
#    就直接返回
#    {'data': {'tasks': None}}
#    """
#    if task is None or task.get("data", {}).get("tasks") is None:
#        return False
#    else:
#        try:
#            task = task.get("data", {}).get("tasks")
#            url = task.get('url')
#            if not url.startswith("http:"):
#                url = "http:" + url
#            print "Going to crawl url: ", url
#            resp = download_page(url, not_proxy=True)
#            if not resp:
#                print "Cannot get current page: %s, sleeping now!!!" % url
#            content, task = parse_detail_page(resp.text, task)
#            with open("result.txt", "a+") as fp:
#                task["title"] = task.get("title")
#                fp.write("%s\n" % json.dumps(task))
#        except:
#            print "Task: %s with Type: %s" % (task, type(task))
#
#    return True


if __name__ == "__main__":
    #pcbaby = PCBabyTaskCrawler(callback=msg_handler,
    #                           ttype="page",
    #                           source="pcbaby")
    #pcbaby.start()
    #gevent.wait()
    #data = json.load(open("seeds.txt"))
    #for cur_task in data:
    #    url = cur_task.get("url")
    #    seed = {"data": {"tasks": {"url": url, "name": "mingxing", "title": cur_task.get("title")}}}
    #    print msg_handler(seed)
    crawler_page("1044283059")
