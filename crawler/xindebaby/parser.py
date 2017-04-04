# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import json
import base64
import lxml.etree

from utils import update_crawler_task
from utils import update_crawler_task_by_rest_api


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

    result["jiandang_status"] = "\n".join(filter(lambda x: u"要求等照片" not in x,
                                          el.xpath("//div[@id='jiandang_status']/div[@class='content']/p/text()")))

    jiandang_process = []
    jiandang_divs = el.xpath("//div[@id='jiandang_process']/table/tbody/tr")
    for jiandang_div in jiandang_divs:
        jiandang_process.append((jiandang_div.xpath("./td/span/text()")[0],
                                 jiandang_div.xpath("./td/text()")))

    result["jiandang_process"] = jiandang_process

    # 将采集到的数据发送到远程服务器
    task.update({"content": result,
                 "result": result,
                 "page": html,
                 "status": "finished"})
    update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(task)))
    return "", result


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


if __name__ == "__main__":
    #parse_detail_page("")
    post_xindebaby_hospital_tasks()