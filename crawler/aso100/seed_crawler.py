# coding=utf8
#

"""
使用selenium采集微信公众号信息的插件
"""

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import json
import time
import random
import base64
import lxml.etree
from selenium import webdriver
from crawler.base_crawler import BaseSeleniumCrawler

from crawler.api_proxy import get_crawler_task

from crawler.http import get_proxy
from crawler.http import generate_proxy

from crawler.api_proxy import update_crawler_task_by_rest_api

from crawler.aso100.parser import parse_cates

proxies = get_proxy()
meta_info = []


class WechatSeleniumCrawler(BaseSeleniumCrawler):
    """ wechat 公众号的采集插件实现 """

    def get_task(self):
        """ 从远程服务器获取wechat的爬虫种子 """
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
            print("开始采集URL: %s" % url)

            result = crawler_by_name()
            update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(result)))
        except:
            print "Task: %s with Type: %s" % (task, type(task))

    return True


def get_proxy_browser():
    """ 获取一个使用代理的浏览器实例 """
    global proxies
    global meta_info

    if not proxies:
        proxies = get_proxy(if_force=True)

    while 1:
        _, meta_info = generate_proxy(proxies)
        host, port, http_method = meta_info
        try:
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', 1)   # 0 => direct connect, 1 => use config defautl to 0
            if http_method == 'HTTP':
                profile.set_preference('network.proxy.socks', host)
                profile.set_preference('network.proxy.socks_port', port)
            elif http_method == 'HTTPS':
                profile.set_preference('network.proxy.ssl', host)
                profile.set_preference('network.proxy.ssl_port', port)
            profile.update_preferences()
            browser = webdriver.Firefox(profile)
            browser.get('http://weixin.sogou.com')
            return browser
        except:
            print meta_info, 'was failed, now is going to choose another one'
            proxies.remove(meta_info)
            print 'Still have ', len(proxies), 'proxies'
            if not proxies:
                proxies = get_proxy(if_force=True)
            _, meta_info = generate_proxy(proxies)


def crawler_by_name():
    """ """
    final_tasks = []
    username = "2269529891@qq.com"
    password = "password1!"
    #browser = get_proxy_browser()

    browser = webdriver.Firefox()

    try:
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

        print("After login, now load the rank page")
        url = "https://aso100.com/rank"
        browser.get(url)
        page_source = browser.page_source

        while 1:
            print("After loading the rank page, now we need find the more btn and click it")
            try:
                more_btn = browser.find_element_by_id("rank-list-more")
            except:
                more_btn = None
                print("Cannot find more btn, looping shutdown")
                break

            time.sleep(random.randint(10, 17))
            # 有查找下一步的按钮，那么就继续按
            more_btn.click()

        print("After click all the more btn, finally we use lxml to parse the page and close the browser")
        tasks = parse_cates("aso100", url, page_source, None)

        with open("seeds.txt", "w") as fp:
            fp.write(json.dumps(tasks.get("aso100")))
    finally:
        browser.close()


if __name__ == '__main__':
    seed = {"data": {"tasks": {"url": "https://aso100.com/rank", "name": "aso100"}}}
    msg_handler(seed)