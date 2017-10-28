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
import random

from crawler.aso100.parser import process_base_info
from crawler.aso100.parser import process_version_info
from crawler.aso100.parser import process_compete_info
from crawler.aso100.parser import process_comment_info
from crawler.aso100.parser import process_aso_compare_info
from crawler.aso100.parser import process_comment_list_info

from crawler.aso100.utils import login_user
from crawler.aso100.utils import get_browser


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

    os.system("mkdir -p /tmp/aso/")
    # 登录用户
    login_user(browser)

    # 登录排名页面
    url = "https://aso100.com/rank"
    browser.get(url)
    time.sleep(random.randint(7, 13))

    keyword_tasks = [#("baseinfo", process_base_info),               # 基本信息
                     #("version", process_version_info),             # 版本信息
                     #("competi", process_compete_info),             # 竞品概况
                     #("keyword", process_aso_compare_info),         # ASO对比
                     ("comment", process_comment_info),             # 评论统计
                     #("commentList", process_comment_list_info),    # 评论详情
            ]

    info_dict = {}
    for keyword, task in keyword_tasks:
        url = base_url % (keyword, appid)
        browser.get(url)
        import ipdb;ipdb.set_trace()
        el = lxml.etree.HTML(browser.page_source)
        task(browser, el, info_dict)
        time.sleep(random.randint(7, 15))

    info_dict.setdefault("baseinfo", {}).update(cur_task)

    # 写入到成功列表
    with open("succ.txt", "a+") as fp:
        fp.write("%s\n" % appid)

    # 写入到结果集合
    with open("task_result.txt", "a+") as fp:
        fp.write("%s\n" % json.dumps(info_dict))

    os.system("rm -rf /tmp/aso/")


def crawler_page():
    """
        采集app详情页面信息

        :return:
    """

    succ_lst = load_succ_tasks()
    tasks = load_tasks(succ_lst)

    browser = get_browser()

    task = random.choice(tasks)
    while task:
        try:
            appid = task["appid"]
            print("Now are going to crawl task: %s" % appid)
            crawl_cur_page(appid, browser, task)
            tasks.remove(task)

            try:
                task = random.choice(tasks)
            except:
                task = None
        finally:
            browser.quit()
            return None


if __name__ == "__main__":
    crawler_page()
