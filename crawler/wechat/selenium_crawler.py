# coding=utf8
#


import time
import random
import argparse
import lxml.etree
from selenium import webdriver

from http import get_proxy
from utils import generate_proxy

import pymongo

db = pymongo.Connection()['wechat_source']

proxies = get_proxy()
meta_info = []


def parse_options():
    """
    解析输入
    """
    parser = argparse.ArgumentParser(description='compare market and site number')
    parser.add_argument('-n', '--name', action='store', dest='name',
                        help=u'需要搜索的微信公众号名称')

    return parser.parse_args()


def parse_cur_source(page_source, cur_id):
    """ """
    el = lxml.etree.HTML(page_source)
    title = el.xpath('//h2[@id="activity-name"]/text()')[0]
    create_on = el.xpath('//em[@class="rich_media_meta rich_media_meta_text"]/text()')[0]
    author = el.xpath('//em[@class="rich_media_meta rich_media_meta_text"]/text()')[1]
    wrap_info = el.xpath('//div[@class="rich_media_thumb_wrp"]')
    if wrap_info:
        wrap_el = wrap_info[0]
        try:
            wrap_image = wrap_el.xpath('./img/@src')[0]
        except:
            wrap_image = wrap_el.xpath('./img/@data-backsrc')[0]
    else:
        wrap_image = ""
    wrap_content = el.xpath('//div[@class="rich_media_content "]')[0]
    content = ""
    for cur_p in wrap_content.xpath('./p/text()'):
        if cur_p:
            content = content + '\n' + cur_p
    print content

    source_info = {'title': title, 'create_on': create_on,
                   'author': author, 'wrap_image': wrap_image,
                   'content': content, 'source': 'wechat', 'cur_id': cur_id}

    cur_record = db.source_code.find_one({'title': source_info.get('title')})
    if not cur_record:
        db.source_code.save(source_info)

    return source_info


def get_proxy_browser():
    """

    """
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


def enter_search_list(browser):
    """ """
    keyword = browser.find_element_by_id('upquery')
    keyword.clear()
    keyword.send_keys(params.name.decode('utf8'))
    btn = browser.find_element_by_class_name('swz2')
    btn.click()

    # open the detail page, it's a new page, so we need to switch the page
    search_result = browser.find_element_by_id('sogou_vr_11002301_box_0')
    search_result.click()
    time.sleep(3)

    return browser


def main(params):
    """ """
    # open the page and enter the search keywords
    print params.name
    browser = get_proxy_browser()
    browser = enter_search_list(browser)

    detail_page_window_id = browser.window_handles[1]
    browser.switch_to_window(detail_page_window_id)
    content_id = 'sogou_vr_11002601_title_%s'

    # open the content page, and add a new window
    try:
        for i in range(10):
            for j in range(10):
                cur_id = content_id % (i * 10 + j)
                try:
                    print cur_id
                    content_btn = browser.find_element_by_id(cur_id)
                    content_btn.click()

                    content_page_window_id = browser.window_handles[2]
                    browser.switch_to_window(content_page_window_id)
                    parse_cur_source(browser.page_source, cur_id)
                    browser.close()
                    time.sleep(random.randint(10, 15))
                    browser.switch_to_window(detail_page_window_id)
                except:
                    params = {'cur_id': cur_id, 'status': 'failed', 'source': 'wechat'}
                    db.source_code.save(params)
                    print 'Got an error with id: ', cur_id
                    continue

            try:
                more_btn = browser.find_element_by_id('wxmore')
            except:
                browser.quit()

            more_btn.click()
        else:
            browser.quit()
    finally:
        browser.quit()


if __name__ == '__main__':
    params = parse_options()
    main(params)