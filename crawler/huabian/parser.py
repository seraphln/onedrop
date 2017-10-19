# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import json
import base64
import lxml.html
import lxml.etree

from crawler.api_proxy import update_crawler_task
from crawler.api_proxy import update_crawler_task_by_rest_api


def parse_cates(cate, url, html, resp, source="huabian"):
    """
        解析分类以及对应的子分类信息

        @param cate: 当前分类的名称
        @type cate: String

        @param url: 当前分类对应的url
        @type url: String

        @param html: 当前url对应的页面信息
        @type html: String

        :return: result_dict
    """
    result_dict = {}

    el = lxml.etree.HTML(html)
    
    els = el.xpath("//div[@class='hb_bmit']")
    for x in els:
        try:
            title, url = x.xpath("./h3/a/@title")[0], x.xpath("./h3/a/@href")[0]
            params = {"url": url,
                      "title": title,
                      "source": source,
                      "ttype": "leaf"}

            print params
            #update_crawler_task(base64.urlsafe_b64encode(json.dumps(params)))

            result_dict.setdefault(cate, []).append(params)
        except Exception as msg:
            print str(msg)
    return result_dict


def parse_detail_page(html, task, source="pcbaby"):
    """
        解析详细的html页面，采集正文信息并发送采集结果到远程服务器
        
        @param html: 需要解析的html页面
        @type html: String

        @param task: 从API服务器拿到的Task Dict
        @type task: Dict

        :return: (content, result)
    """
    el = lxml.etree.HTML(html)

    content_el = el.xpath("//div[@class='hb_content']")[0]
    content = lxml.html.tostring(content_el)

    # 将采集到的数据发送到远程服务器
    task.update({"content": content,
                 "page": html,
                 "source": source,
                 "status": "finished"})
    #update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(task)))
    return content, task


if __name__ == "__main__":
    parse_detail_page("")