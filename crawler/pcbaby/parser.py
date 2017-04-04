# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import json
import base64
import lxml.etree

from crawler.api_proxy import update_crawler_task
from crawler.api_proxy import update_crawler_task_by_rest_api


def parse_cates(cate, url, html, resp):
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
    cates = el.xpath("//div[@class='baike-th']")
    sub_cates = el.xpath("//div[@class='baike-tb clearfix']")

    print "Starting to crawl cates with length: %s" % len(cates)
    for i, cate in enumerate(cates):
        print "Starting to crawl cate: %s, %s of %s" % (cate, i, len(cates))
        cate_name = cate.xpath("./div[@class='baike-th-name']/text()")[0]
        # 主分类
        cate_dict = {}

        # 二级分类
        cur_sub_cates = sub_cates[i].xpath("./div[@class='baike-tb-dl']")
        for cur_sub_cate in cur_sub_cates:
            sub_cate_name = cur_sub_cate.xpath("./dl/dt/a/text()")[0]
            sub_cate_dict = cate_dict.setdefault(sub_cate_name, {})
            sub_cate_dict.update({"name": sub_cate_name,
                                  "url": cur_sub_cate.xpath("./dl/dt/a/@href")[0]})

            # 三级分类
            third_cates = cur_sub_cate.xpath("./dl/dd/span")
            for i, third_cate in enumerate(third_cates):
                print "Starting to crawl third_cate: %s, %s of %s" % (third_cate, i, len(third_cates))
                third_cate_name = third_cate.xpath("./a/text()")[0]
                third_cate_url = third_cate.xpath("./a/@href")[0]
                sub_cate_dict.setdefault("third_cates", []).append({"name": third_cate_name,
                                                                    "url": third_cate_url})

                # 发送分类信息到线上
                params = {"name": third_cate_name,
                          "category": sub_cate_name,
                          "parent_category": cate_name,
                          "url": third_cate_url,
                          "ttype": "leaf"}
                update_crawler_task(base64.urlsafe_b64encode(json.dumps(params)))

        result_dict[cate_name] = cate_dict
        print "Cate: %s, %s of %s" % (cate, i, len(cates))
    print "Done of crawl cates with length: %s" % len(cates)
    return result_dict


def parse_detail_page(html, task):
    """
        解析详细的html页面，采集正文信息并发送采集结果到远程服务器
        
        @param html: 需要解析的html页面
        @type html: String

        @param task: 从API服务器拿到的Task Dict
        @type task: Dict

        :return: (content, result)
    """
    el = lxml.etree.HTML(html)
    els = el.xpath("//div[@class='mb30 border shadow mt30']/div[@class='l-tbody']")
    content = ""
    result = {}

    for cur_el in els:
        tmp_content = ""
        tmp_title = cur_el.xpath("./p[@class='m-th pt22']/a/text()")[0]
        tmp_content_els = cur_el.xpath("./div[@class='art-text']/p")

        for tmp_content_el in tmp_content_els:
            tmp_record = ""
            try:
                tmp_record = tmp_content_el.xpath("./strong/text()")[0]
            except:
                pass

            if not tmp_record:
                try:
                    tmp_record = tmp_content_el.xpath("./text()")[0]
                except:
                    pass

            if tmp_record:
                tmp_content = "%s\n%s" % (tmp_content, tmp_record)

        if tmp_content and tmp_title:
            content = "%s\n%s\n%s" % (content, tmp_title, tmp_content)
            result[tmp_title] = tmp_content

    # 将采集到的数据发送到远程服务器
    task.update({"content": content,
                 "result": result,
                 "page": html,
                 "status": "finished"})
    update_crawler_task_by_rest_api(base64.urlsafe_b64encode(json.dumps(task)))
    return content, result


if __name__ == "__main__":
    parse_detail_page("")