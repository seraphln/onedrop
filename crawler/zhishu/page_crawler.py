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

from crawler.zhishu.parser import parse_page_info

from crawler.zhishu.utils import get_browser

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


def crawl_cur_page(keyword, browser, cur_task):
    """
    爬取当前页面，并将结果写入到文件中

    @param keyword: 需要采集的关键词
    @type appid: String

    @param browser: 浏览器实例
    @type browser: webdriver

    @param cur_task: 当前任务
    @type cur_task: Dict

    :return:
    """

    # 登录排名页面
    url = "http://zhishu.baidu.com/"
    browser.get(url)

    keyword_input = browser.find_element_by_id("schword")
    keyword_input.send_keys(keyword)
    time.sleep(random.randint(3, 7))

    submit = browser.find_element_by_id("searchWords")
    submit.click()

    info_dict = {"keyword": keyword}
    parse_page_info(info_dict, browser)

    cur_task.update({"content": "",
                     "result": info_dict,
                     "page": browser.page_source})

    update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(cur_task)))


def get_task():
    """ 获取一个采集的任务 """
    task = get_crawler_task("aso100")
    """
    {'data': {'tasks': {u'status': u'running',
                        u'category': u'zhishu',
                        u'name': u'彩钢板',
                        u'url': u'zhishu.baidu.com',
                        u'ttype': u'leaf',
                        u'id': u'Q3Jhd2xlclRhc2tzOjczMDg5NA=='}}}
    """
    task = task.get("data", {}).get("tasks")
    task["source"] = "zhishu"
    return task


def crawler_page():
    """
        采集app详情页面信息

        :return:
    """
    task = get_task()

    browser = get_browser()

    # 登录用户
    # login_user(browser)

    try:
        while task is not None:
            print(task)
            keyword = task["name"]
            print("Now are going to crawl task: %s" % keyword)
            crawl_cur_page(keyword, browser, task)
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
