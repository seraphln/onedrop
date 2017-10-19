# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

import json
import base64
import lxml.html
import lxml.etree

from lxml.html import clean

from crawler.http import download_page

from crawler.api_proxy import update_crawler_task
from crawler.api_proxy import update_crawler_task_by_rest_api


def parse_detail_page(html, task):
    """ 解析详细的html页面，采集正文信息 """
    el = lxml.etree.HTML(html)
    result = {}

    base_url = "http://xindebaby.com"

    summary_div = el.xpath("//div[@id='summary']")[0]
    result = {"avatar": "%s%s" % (base_url, summary_div.xpath("./div[@class='header']/a/img/@src")[0]),
              "name": summary_div.xpath("./div[@class='header']/div[@class='info']/h1/text()")[0],
              "tags": summary_div.xpath("./div[@class='header']/div[@class='info']/p/a/text()"),
              "address": summary_div.xpath("./div[@class='header']/div[@class='info']/a/text()")[0],
              "capability": {"enable": summary_div.xpath("./div[@class='capability']/a[@class='ok']/text()"),
                             "disable": summary_div.xpath("./div[@class='capability']/a[@class='no']/text()")}}
    expense_keywords = summary_div.xpath("./div[@class='expense']/text()")
    expense_costs = summary_div.xpath("./div[@class='expense']/span/text()")
    result["expense"] = zip(expense_keywords, expense_costs)

    doctor_lst = []
    doctors = el.xpath("//div[@id='doctors']/a/ul/li")
    for doctor in doctors:
        doctor_lst.append({"avatar": "%s%s" % (base_url, doctor.xpath("./img/@src")[0]),
                           "name": doctor.xpath("./span/text()")[0]})

    result["doctors"] = doctor_lst

    ret = download_intro_page(el, base_url)
    result.update(ret)

    result["jiandang_status"] = "\n".join(filter(lambda x: u"要求等照片" not in x,
                                          el.xpath("//div[@id='jiandang_status']/div[@class='content']/p/text()")))

    jiandang_process = []
    jiandang_divs = el.xpath("//div[@id='jiandang_process']/table/tbody/tr")
    jiandang_divs = jiandang_divs or el.xpath("//div[@id='jiandang_process']/table/tr")
    for jiandang_div in jiandang_divs:
        jiandang_process.append((jiandang_div.xpath("./td/span/text()")[0],
                                 jiandang_div.xpath("./td/text()")[0]))

    result["jiandang_process"] = jiandang_process

    # 将采集到的数据发送到远程服务器
    task.update({"content": result,
                 "result": result,
                 "page": html,
                 "source": "xindebaby",
                 "status": "finished"})
    update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(task)))
    return "", result


def download_intro_page(el, base_url):
    """
        获取页面中的简介信息，如果有详细信息页面，则下载详细信息页面并把内容解析出来
    """
    try:
        intro_div = el.xpath("//div[@id='intro']")[0]
        intro = intro_div.xpath("./div[@class='content']/p/text()")[0]

        # 获取详细信息url
        intro_url = intro_div.xpath("//div[@id='intro']/div/p/a/@href")[0]
        intro_url = base_url + intro_url
        # 下载详细信息
        intro_detail_resp = download_page(intro_url)

        # 解析详细信息并把结果返回
        html = intro_detail_resp.text
        c = clean.Cleaner(style=True, scripts=True,
                          page_structure=False, safe_attrs_only=False)
        intro_detail = c.clean_html(html)
    except:
        html = ""
        intro = ""
        intro_detail = ""

    return {"desc": intro, "desc_detail": intro_detail, "desc_ori": html}



def post_xindebaby_hospital_tasks():
    """
        创建xindebaby的医院采集任务
    """
    data = map(lambda x: x.strip().split(","), open("tasks.txt").readlines())

    for category, name, url in data:
        params = {"name": name,
                  "category": category,
                  "url": url,
                  "ttype": "leaf",
                  "source": "xindebaby",
                  "parent_category": u"医院信息"}
        update_crawler_task(base64.urlsafe_b64encode(json.dumps(params)))
        print params


def parse_page(html, task):
    """ 解析页面，获取title, keywords, desc """

    el = lxml.etree.HTML(html)
    result = {}
    try:
        result.update({"title": el.xpath("//title/text()")[0]})
    except:
        pass
    try:
        result.update({"keywords": el.xpath("//meta[@name='keywords']/@content")[0]})
    except:
        pass
    try:
        result.update({"desc": el.xpath("//meta[@name='description']/@content")[0]})
    except:
        pass

    # 将采集到的数据发送到远程服务器
    task.update({"result": result})
    #update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(task)))
    return "", task

def post_yjs_tasks():
    """
        创建yjs的采集任务
    """
    data = map(lambda x: x.strip(), open("dns_records.txt").readlines())

    for url in data:
        category = "yjs"
        name = "yjs"

        params = {"name": name,
                  "category": category,
                  "url": url,
                  "ttype": "leaf",
                  "source": "yjs",
                  "parent_category": u"yjs"}
        update_crawler_task(base64.urlsafe_b64encode(json.dumps(params)))
        print params


if __name__ == "__main__":
    #parse_detail_page("")
    #post_xindebaby_hospital_tasks()
    post_yjs_tasks()