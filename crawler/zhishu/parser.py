# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import os
import re
import json
import time
import base64
import lxml.html
import lxml.etree

from crawler.aso100.utils import generate_fname
from crawler.aso100.excel import extract_comment_xlsx
from crawler.aso100.excel import extract_keywords_xlsx

from crawler.api_proxy import update_crawler_task
from crawler.api_proxy import update_crawler_task_by_rest_api


INT_RE = re.compile("\d+")
API_RE = re.compile("{[\S\s]+}")
BASE_URL = "http://aso100.com"


def parse_page_info(info_dict, browser):
    """
    解析页面信息

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict
    
    """
    el = lxml.etree.HTML(browser.page_source)
    seven_days_info = {}
    thirty_days_info = {}

    basic_info = el.xpath("//table[@class='mtable profWagv']")[0]
    seven_days_info = parse_basic_info(basic_info)



def parse_basic_info(basic_info):
    """ 解析基本信息 """
    tds = basic_info.xpath("./tr/[1]/td")

    total_day_value = tds[1].xpath("./div/span/[1]/")




def process_comment_list_info(browser, el, info_dict):
    """
    处理评论详情页面

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict

    :return:
    """
    comments = []
    try:
        trs = el.xpath("//div[@class='comment']/table/tbody/tr")

        for tr in trs:
            rank = tr.xpath("./td[@class='reting']/p")[0].xpath("./span/@style")[0]
            rank = INT_RE.findall(rank)[0]

            title = tr.xpath("./td")[1].xpath("./p")[0].xpath("./strong/text()")[0]
            author = tr.xpath("./td")[1].xpath("./p")[0].xpath("./a/text()")[0]
            content = tr.xpath("./td")[1].xpath("./div/text()")[0]
            comment_date = tr.xpath("./td")[2].xpath("./text()")[0]

            cur_comment = {"rank": rank,
                           "title": title,
                           "author": author,
                           "content": content,
                           "comment_date": comment_date}

            comments.append(cur_comment)

        info_dict.setdefault("comment_lst", {}).update({"comments": comments})
    except Exception as msg:
        print str(msg)


if __name__ == "__main__":
    parse_cates("")