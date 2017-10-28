# coding=utf-8
#


"""
aso100爬虫相关的功能函数集合
"""

import json
import time
import random

from datetime import datetime
from datetime import timedelta

from selenium import webdriver


def generate_fname(appname, ttype="keyword"):
    """
    生成文件名

    @param appname: 给定的应用名
    @type appname: String

    @param ttype: 文件类型
    @type ttype: String

    :return:
    """
    now = datetime.now()
    name_mapper = {"keyword": u"关键词覆盖数据",
                   "comment": u"评论详情"}

    if ttype == "keyword":
        fname = u"/tmp/aso/%s_%s_%s.xlsx" % (appname,
                                             name_mapper[ttype],
                                             now.strftime("%Y%m%d"))
    elif ttype == "comment":
        fname = u"/tmp/aso/%s_%s_%s_%s.xlsx" % (appname,
                                                name_mapper[ttype],
                                                (now-timedelta(days=7)).strftime("%Y%m%d"),
                                                now.strftime("%Y%m%d"))

    return fname


def get_browser():
    """
        获取浏览器实例

        :return: browser
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": "/tmp/aso/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})

    browser = webdriver.Chrome(chrome_options=options)

    return browser


def login_user(browser):
    """
        登录用户

        @param browser: selenium实例
        @type browser: webdriver.Chrome

        :return:
    """
    users = json.load(open("users.txt"))
    user = random.choice(users)
    username = user.get("username")
    password = user.get("password")

    # 打开首页
    index_url = "https://aso100.com"
    browser.get(index_url)
    time.sleep(random.randint(3, 7))

    # 如果需要，则登录
    if browser.page_source.find("account/signin") != -1:
        print("Need login first, now running login module")
        browser.get("http://aso100.com/account/signin")

        username_btn = browser.find_element_by_id("username")
        password_btn = browser.find_element_by_id("password")

        username_btn.send_keys(username)
        password_btn.send_keys(password)

        print("Finished send username and password, now sleeping to wait for click login")
        time.sleep(random.randint(10, 17))
        submit_btn = browser.find_element_by_id("submit")
        submit_btn.click()


