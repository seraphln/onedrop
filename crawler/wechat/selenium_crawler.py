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
import base64
import lxml.etree
from selenium import webdriver
from crawler.base_crawler import BaseSeleniumCrawler

from crawler.api_proxy import get_crawler_task

from crawler.http import get_proxy
from crawler.http import generate_proxy

from crawler.wechat.parser import parse_user_info
from crawler.wechat.parser import parse_page_content
from crawler.wechat.parser import find_correct_element_url

from crawler.api_proxy import update_crawler_task_by_rest_api

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
            name = task.get('name')
            print "开始采集公众号: ", name

            result = crawler_by_name(name)
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


def enter_search_list(browser, name):
    """ """
    keyword = browser.find_element_by_id('upquery')
    keyword.clear()
    keyword.send_keys(name)
    btn = browser.find_element_by_class_name('swz2')
    btn.click()

    # open the detail page, it's a new page, so we need to switch the page
    search_result = browser.find_element_by_id('sogou_vr_11002301_box_0')
    search_result.click()
    time.sleep(3)

    return browser


def crawler_by_name(name):
    """ """
    browser = get_proxy_browser()
    browser = enter_search_list(browser, name)

    detail_page_window_id = browser.window_handles[0]
    browser.switch_to_window(detail_page_window_id)

    el = lxml.etree.HTML(browser.page_source)
    detail_url = find_correct_element_url(name, el, browser.page_source)

    try:
        browser.get(detail_url)
        # 保存当前的id
        detail_page_window_id = browser.window_handles[0]

        el = lxml.etree.HTML(browser.page_source) 
        user_info, content_lst, content_urls = parse_user_info(el, browser.page_source)

        contents = []
        for target_url in content_urls:
            browser.get(target_url)
            el = lxml.etree.HTML(browser.page_source)
            result = parse_page_content(el, browser.page_source)
            contents.append(result)

        result = {"user_info": user_info,
                  "content_lst": content_lst,
                  "contents": contents}
    finally:
        browser.quit()


if __name__ == '__main__':
    crawler_by_name(u"小道消息")