# coding=utf8
#


"""
huabian.com的导航页面爬虫实现
"""
from gevent import monkey
monkey.patch_all()

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import gevent

import json
import time
from crawler.http import download_page
from crawler.base_crawler import BaseCrawler
from crawler.huabian.parser import parse_cates

from crawler.api_proxy import get_crawler_seed

from crawler.huabian.page_crawler import msg_handler as page_msg_handler


class HuaBianSeedCrawler(BaseCrawler):
    """ huabian.com导航页面对应的爬虫实现 """

    def get_task(self):
        """ 从远程服务器获取pcbaby的爬虫种子 """
        return get_crawler_seed(self.source)


def msg_handler(seed):
    """
    检查seed，如果获取到的seed示例有问题的话
    就直接返回
    """
    if seed is None or seed.get("data", {}).get("seeds") is None:
        return
    else:
        try:
            task_lst = []
            seed = seed.get("data", {}).get("seeds")
            url = seed.get('url')
            for i in range(1, 6):
                data = {"offset": i, "type": "list", "dataid": 114}
                time.sleep(3)
                resp = download_page(url, data=data)
                if not resp:
                    print "Cannot get current page: %s, Going home now!!!" % url
                    return ""
                res = parse_cates(seed.get("name"), url, resp.text, resp)
                task_lst.extend(res.get("mingxing"))

            with open("seeds.txt", "w") as fp:
                fp.write(json.dumps(task_lst))
        except:
            print "Seed: %s with Type: %s" % (seed, type(seed))


if __name__ == "__main__":
    #pcbaby = HuaBianSeedCrawler(callback=msg_handler, ttype="seed")
    #pcbaby.start()
    #gevent.wait()
    seed = {"data": {"seeds": {"url": "http://www.huabian.com/mingxing/", "name": "mingxing"}}}
    print msg_handler(seed)

    data = json.load(open("seeds.txt"))
    for cur_task in data:
        url = cur_task.get("url")
        seed = {"data": {"tasks": {"url": url, "name": "mingxing", "title": cur_task.get("title")}}}
        print page_msg_handler(seed)
