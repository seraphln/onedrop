# coding=utf8
#


'''
包括所有的http相关的函数
'''

import os
import time
import random
import requests
import httplib2
import lxml.etree


LOCAL_PROXY_IP_FILE_NAME = 'proxies.txt'


def default_headers(headers=None):
    if headers is None:
        headers = dict()

    if 'User-Agent' not in headers:
        headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17"

    if 'Accept' not in headers:
        headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

    if 'Accept-Encoding' not in headers:
        headers['Accept-Encoding'] = "gzip,deflate"

    if 'Accept-Language' not in headers:
        headers['Accept-Language'] = "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3"

    if 'Connection' not in headers:
        headers['Connection'] = "keep-alive"

    headers['Cache-Control'] = "max-age=0"
    return headers


def get_proxy(if_force=False):
    proxies = []
    content = None
    if os.path.isfile(LOCAL_PROXY_IP_FILE_NAME) and not if_force:
        proxies = map(lambda x: x.strip().split('\t'), open(LOCAL_PROXY_IP_FILE_NAME).readlines())
        return proxies

    headers = default_headers()
    if not content:
        url = 'http://www.xicidaili.com/'
        headers.update({"Accept-Encoding": "gzip, deflate, sdch",
                        "Host": 'www.xicidaili.com',
                        "Connection": "keep-alive",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Upgrade-Insecure-Requests": "1"})
        print headers
        resp = requests.get(url, headers=headers)
        _cookie = resp.cookies
        try:
            headers.update({'Referer': url})
            url = "http://www.xicidaili.com/nn"
            resp = requests.request('GET', url, headers=headers, cookies=_cookie)
        except Exception, e:
            print e
    proxies = []
    el = lxml.etree.HTML(resp.text)
    for item in el.xpath('//table[@id="ip_list"]/tr')[2:]:
        tmp_lst = [x.xpath('./text()') for x in item.xpath('./td')]
        tmp_lst = filter(lambda x: x, tmp_lst)
        if tmp_lst[4][0] in ['HTTP', 'HTTPS']:
            proxies.append((tmp_lst[0][0], tmp_lst[1][0], tmp_lst[4][0]))

    with open(LOCAL_PROXY_IP_FILE_NAME, 'w') as fp:
        for ip, port, method in proxies:
            fp.write('%s\t%s\t%s\n' % (ip, port, method))

    return proxies


def remove_proxy(host, port, http_method, proxies):
    """ 从proxies列表中移除当前传入的代理ip信息 """
    try:
        proxies.remove((str(host), str(port), str(http_method)))
    except ValueError:
        try:
           proxies.remove([str(host), str(port), str(http_method)])
        except:
            print host, port, http_method, proxies

    if not proxies:
        proxies = get_proxy(if_force=True)


def download_page(url, headers=None, timeout=1, proxies=None, not_proxy=False):
    ''' 下载页面的具体函数 '''

    if not proxies:
        proxies = get_proxy()

    if not headers:
        headers = default_headers()

    global cookies

    # 最多执行100次
    counter = 100

    while 1:
        host, port, http_method = random.choice(proxies)
        proxy_dict = {http_method.lower(): 'http://%s:%s' % (host, port)}
        query_dict = {'url': url,
                      'headers': headers,
                      'timeout': timeout,
                      'proxies': proxy_dict}
        try:
            if cookies:
                query_dict['cookies'] = cookies
            if not_proxy:
                query_dict.pop("proxies")
            resp = requests.get(**query_dict)
            if resp.status_code != 200:
                print "Got an except resp code: %s" % resp.status_code
                continue

            if "Unauthorized" in resp.text or "unauthorized" in resp.text or u"请输入验证码" in resp.text:
                print "Got an exception in downloading page"
                remove_proxy(host, port, http_method, proxies)
                continue

            if resp.text:
                _cookie = resp.cookies
                break
        except Exception as e:
            if 'timeout' in str(e):
                remove_proxy(host, port, http_method, proxies)
            elif 'Connection aborted.' in str(e):
                remove_proxy(host, port, http_method, proxies)
                time.sleep(3)
            else:
                counter -= 1
                remove_proxy(host, port, http_method, proxies)
                if counter <= 0:
                    return ""

            if not proxies:
                proxies = get_proxy(if_force=True)

    return resp


cookies = None


if __name__ == "__main__":
    proxies = get_proxy()
