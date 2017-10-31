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
from selenium import webdriver

from crawler.http import get_proxy
from crawler.http import generate_proxy

from crawler.aso100.parser import parse_cates

from crawler.aso100.utils import login_user
from crawler.aso100.utils import get_browser

proxies = get_proxy()
meta_info = []


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


def crawl_tasks():
    """ 采集任务列表 """

    # 加载用户名和密码列表
    # 随机从数据列表中选择一个用户名和密码来使用
    browser = get_browser()

    try:
        login_user(browser)

        base_url = "https://aso100.com"
        browser.get(base_url)
        time.sleep(random.randint(3, 7))

        print("After login, now load the rank page")
        url = "https://aso100.com/rank"
        browser.get(url)

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
            try:
                more_btn.click()
            except:
                break

        page_source = browser.page_source
        print("After click all the more btn, finally we use lxml to parse the page and close the browser")
        tasks = parse_cates("aso100", url, page_source, None)

        with open("seeds.txt", "w") as fp:
            fp.write(json.dumps(tasks.get("aso100")))
    finally:
        browser.quit()


if __name__ == '__main__':
    crawl_tasks()