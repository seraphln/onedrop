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

import os
import json
import lxml
import time
import base64
import random

from crawler.aso100.parser import process_base_info
from crawler.aso100.parser import process_version_info
from crawler.aso100.parser import process_compete_info
from crawler.aso100.parser import process_comment_info
from crawler.aso100.parser import process_aso_compare_info
from crawler.aso100.parser import process_comment_list_info

from crawler.aso100.utils import login_user
from crawler.aso100.utils import get_browser

from crawler.api_proxy import get_crawler_task
from crawler.api_proxy import update_crawler_task_by_rest_api

#import pyvirtualdisplay

#display = pyvirtualdisplay.Display(visible=False, size=(800,600))
#display.start()


def load_tasks(success_lst=None):
    """
        读取任务列表

        @param success_lst: 成功的列表
        @type success_lst: List

        :return:
    """
    tasks = []
    data = open("seeds.txt").readlines()
    data = json.loads(data[0])

    for task in data:
        if "appid" not in task:
            url = task.get("url")
            appid = url.split("/")[-3]
            task["appid"] = appid
        else:
            appid = task["appid"]

        if appid not in success_lst:
            tasks.append(task)

    return tasks


def load_succ_tasks():
    """
        获取已经抓取成功的任务列表
        
        :return: List
    """
    try:
        return map(lambda x: x.strip(), open("succ.txt").readlines())
    except:
        return []


def crawl_cur_page(appid, browser, cur_task):
    """
    爬取当前页面，并将结果写入到文件中

    @param appid: 需要采集的app的id
    @type appid: String

    @param browser: 浏览器实例
    @type browser: webdriver

    @param cur_task: 当前任务
    @type cur_task: Dict

    :return:
    """
    base_url = "https://aso100.com/app/%s/appid/%s/country/cn"

    #os.system("mkdir -p /tmp/aso/")

    # 登录排名页面
    url = "https://aso100.com/rank"
    browser.get(url)
    time.sleep(random.randint(7, 13))

    keyword_tasks = [("baseinfo", process_base_info),               # 基本信息
                     ("version", process_version_info),             # 版本信息
                     ("competi", process_compete_info),             # 竞品概况
                     ("keyword", process_aso_compare_info),         # ASO对比
                     ("comment", process_comment_info),             # 评论统计
                     ("commentList", process_comment_list_info),    # 评论详情
            ]

    info_dict = {}
    for keyword, task in keyword_tasks:
        url = base_url % (keyword, appid)
        browser.get(url)
        el = lxml.etree.HTML(browser.page_source)
        task(browser, el, info_dict)
        #time.sleep(random.randint(7, 15))
        time.sleep(random.randint(1, 3))

    print cur_task
    cur_task.update({"content": "",
                     "result": info_dict,
                     "page": browser.page_source})
    #info_dict.updfate(cur_task)

    # 写入到成功列表
    #with open("succ.txt", "a+") as fp:
    #    fp.write("%s\n" % appid)

    #import ipdb;ipdb.set_trace()
    #update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(info_dict)))
    update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(cur_task)))

    # 写入到结果集合
    #with open("task_result.txt", "a+") as fp:
    #    fp.write("%s\n" % json.dumps(info_dict))

    #os.system("rm -rf /tmp/aso/")


def get_task():
    """ 获取一个采集的任务 """
    task = get_crawler_task("aso100")
    """
    {'data': {'tasks': {u'status': u'running',
                        u'category': u'aso100',
                        u'name': u'\u6dd8\u5b9d-\u53cc\u5341\u4e00\u8d2d\u7269\uff0c\u79fb\u52a8\u751f\u6d3b\u793e\u533a',
                        u'url': u'http://aso100.com/app/rank/appid/387682726/country/cn',
                        u'ttype': u'leaf',
                        u'id': u'Q3Jhd2xlclRhc2tzOjczMDg5NA=='}}}
    """
    task = task.get("data", {}).get("tasks")
    if "appid" not in task:
        url = task.get("url")
        appid = url.split("/")[-3]
        task["appid"] = appid
    else:
        appid = task["appid"]

    task["source"] = "aso100"
    return task


def crawler_page():
    """
        采集app详情页面信息

        :return:
    """

#    succ_lst = load_succ_tasks()
#    tasks = load_tasks(succ_lst)
    task = get_task()

    browser = get_browser()

    # 登录用户
    login_user(browser)

    #task = random.choice(tasks)

    try:
        while task is not None:
            print(task)
            appid = task["appid"]
            print("Now are going to crawl task: %s" % appid)
            crawl_cur_page(appid, browser, task)
            print("After finished crawling task: %s" % json.dumps(task))

            try:
                task = get_task()
            except Exception as msg:
                print("Cannot get new task")
                print str(msg)
                task = None

            print("Here are new task: %s" % json.dumps(task))
    except Exception as msg:
        print("Got an error with crawl data")
        print str(msg)
    finally:
        browser.quit()
        return None


if __name__ == "__main__":
    crawler_page()
