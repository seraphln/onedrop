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


def parse_cates(cate, url, html, resp, source="aso100"):
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
    
    els = el.xpath("//div[@class='container']/div[@class='rank-list']/div[@class='row']/div[@class='col-md-2']")
    base_url = "http://aso100.com"

    for x in els:
        try:
            url = x.xpath("./div[@class='thumbnail']/a/@href")[0]
            url = base_url + url

            logo = x.xpath("./div[@class='thumbnail']/a/img/@src")[0]

            cur_seq = x.xpath("./div[@class='thumbnail']/a/div[@class='caption']/h5/text()")[0]

            seq, name = cur_seq.split(".")[:2]
            company = x.xpath("./div[@class='thumbnail']/a/div[@class='caption']/h6/text()")[0]

            try:
                rank_el = x.xpath("./div[@class='thumbnail']/a/div[@class='caption']/h6/span")[0]
                rank = rank_el.text()
                ranking_changes = 1 if "glyphicon-triangle-top" in rank_el.xpath("./@class")[0] else -1
            except:
                try:
                    # 取不到的时候，可能是霸榜
                    rank = x.xpath("./div[@class='thumbnail']/a/div[@class='caption']/h6[1]/@data-original-title")[0]
                    ranking_changes = 0
                except:
                    try:
                        # 或者是没变化
                        rank = x.xpath("./div[@class='thumbnail']/a/div[@class='caption']/h6[1]/text()")[0]
                        ranking_changes = 0
                    except:
                        rank = ""
                        ranking_changes = 0

            params = {"url": url,
                      "logo": logo,
                      "seq": seq,
                      "name": name,
                      "company": company,
                      "rank": rank,
                      "ranking_changes": ranking_changes,
                      "ttype": "leaf"}

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