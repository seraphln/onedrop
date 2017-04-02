# coding=utf8
#


"""
太平洋亲子网的爬虫实现

目前将爬虫分为如下几个部分：
1. 导航栏的采集，包括：怀孕、育儿、营养、生活、用品、生男生女、食谱、用品常识
2. 二级导航，包括：孕育周刊、母婴检查、疾病防疫、营养饮食、保健护理
3. 三级导航，包括: 备孕百科及子分类等
"""

import json
import time
import requests

from parser import parse_cates
from parser import parse_detail_page

from http import download_page

from utils import get_crawler_seed
from utils import get_crawler_task
 

def crawl_page(name, url):
    """ 分析当前页面，拿到所有的URL并把URL写入到远程的中心服务器 """
    resp = download_page(url)
    if not resp:
        return ""
    print "Starting to crawl cate: %s with url: %s" % (name, url)
    with open("banner_cates/%s.txt" % name, "w") as fp:
        data = json.dumps(parse_cates(name, url, resp.text))
        fp.write(json.dumps(data))

    print "Done of crawl cate: %s with url: %s" % (name, url)


def crawl_detail_page(name, url):
    """ 采集具体的页面 """
    resp = requests.get(url)
    content, result = parse_detail_page(resp.text)
    print resp.text


#def PCBabyCrawler(BaseCrawler):
#    """ baike.pcbaby.com.cn对应的爬虫实现 """
#
#    def task_consumer_worker(self):
#        """
#            获取一个seed URL，爬取页面并判断是否是叶子页面，
#            如果是，则发送到远程的中心服务的URL队列，并且类型为leaf。
#            如果是依然是种子节点，则发送到远程中心服务的URL队列，类型为seed
#        """
#        pass
#
#    def get_task(self):
#        """ 从远程服务器获取pcbaby的爬虫种子 """
#        return "http://baike.pcbaby.com.cn/yunqian.html"


def backend():
    """
    1. 启动爬虫
    2. 获取要爬取的seed
    [{u'node': {u'url': u'http://baike.pcbaby.com.cn/fenmian.html',
                u'source': u'\u592a\u5e73\u6d0b\u4eb2\u5b50\u7f51',
                u'status': u'running',
                u'id': u'Q3Jhd2xlclNlZWRzOjM=',
                u'name': u'\u4eb2\u5b50\u767e\u79d1\u5206\u5a29'}}]
    3. 抓取seed页面，并把分类信息发送到服务器
    """
    while 1:
        seed = get_crawler_seed()
        if not seed:
            print "No more seed! Going home now!!!"
            return
        else:
            seed = seed.get("data", {}).get("seeds")
            url = seed.get('url')
            resp = download_page(url)
            if not resp:
                print "Cannot get current page: %s, Going home now!!!" % url
                return ""
            parse_cates(seed.get("name"), url, resp.text, resp)


def page_backend():
    """
    1. 启动爬虫
    2. 获取要爬取的url
    {'data': {'tasks': {u'url': u'http://baike.pcbaby.com.cn/qzbd/4495.html',
                        u'status': u'running',
                        u'id': u'Q3Jhd2xlclRhc2tzOjM=',
                        u'name': u'\u4e0d\u5b55\u4e0d\u80b2\u68c0\u67e5'}}}
    3. 抓取url页面，并把结果信息发送到服务器
    """
    while 1:
        try:
            task = get_crawler_task()
            if not task:
                print "No more seed! Going home now!!!"
                return
            else:
                task = task.get("data", {}).get("tasks")
                url = task.get('url')
                resp = download_page(url)
                if not resp:
                    print "Cannot get current page: %s, sleeping now!!!" % url
                parse_detail_page(resp.text, task)
        except:
            time.sleep(3)


if __name__ == "__main__":

    #url = "http://baike.pcbaby.com.cn/yunqian.html"
    #url_dict = {"yunqian": "http://baike.pcbaby.com.cn/yunqian.html",
    #            "yunqi": "http://baike.pcbaby.com.cn/yunqi.html",
    #            #"fenmian": "http://baike.pcbaby.com.cn/fenmian.html",
    #            "yuezi": "http://baike.pcbaby.com.cn/yuezi.html"}
    #            #"xinshenger": "http://baike.pcbaby.com.cn/xinshenger.html"}
    #            #"yinger": "http://baike.pcbaby.com.cn/yinger.html",
    #            #"youer": "http://baike.pcbaby.com.cn/youer.html",
    #            #"xuelingqian": "http://baike.pcbaby.com.cn/xuelingqian.html",
    #            #"meishi": "http://baike.pcbaby.com.cn/meishi.html",
    #            #"shenghuo": "http://baike.pcbaby.com.cn/shenghuo.html",
    #            #"yongpin": "http://baike.pcbaby.com.cn/yongpin.html"}
    #for name, url in url_dict.iteritems():
    #    crawl_page(name, url)

    #url = "http://baike.pcbaby.com.cn/qzbd/4495.html"
    #crawl_detail_page("", url)
    #backend()
    page_backend()
