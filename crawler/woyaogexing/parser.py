# coding=utf8
#


"""
woyaogexing.com相关的页面解析用功能函数
"""


import json
import base64
import lxml.etree

from crawler.api_proxy import update_crawler_task


def parse_cates(name, url, resp, source="woyaogexing"):
    """
        解析页面的url，并判断是否需要继续翻页
    """

    result_lst =  []
    base_url = "http://www.woyaogexing.com"
    el = lxml.etree.HTML(resp.text)
    contents = el.xpath("//div[@id='main']/div[@class='list-main mt10 cl']/div[@class='list-left z']/div[@class='pMain']/div")

    for content in contents:
        result = {"category": u"QQ头像",
                  "parent_category": u"我要个性",
                  "source": source,
                  "ttype": "leaf"}

        # url = /touxiang/nv/2017/474876.html
        url = content.xpath("./a[@class='imgTitle']/@href")[0]
        url = base_url + url

        name = content.xpath("./a/text()")[0]

        result.update({"url": url, "name": name})
        update_crawler_task(base64.urlsafe_b64encode(json.dumps(result)))
        result_lst.append(result)

    next_els = el.xpath("//div[@class='pageNum wp']/div/a/text()")
    # 下一页
    if_next = u'\xe4\xb8\x8b\xe4\xb8\x80\xe9\xa1\xb5' in resp.text

    return result_lst, if_next
