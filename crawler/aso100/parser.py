# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import re
import lxml.html
import lxml.etree

from crawler.aso100.utils import generate_fname
from crawler.aso100.excel import extract_keywords_xlsx

from crawler.api_proxy import update_crawler_task
from crawler.api_proxy import update_crawler_task_by_rest_api


INT_RE = re.compile("\d")
BASE_URL = "http://aso100.com"


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


def process_base_info(browser, el, info_dict):
    """
    解析app的基本信息

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict

    :return:
    """
    header_el = el.xpath("//div[@class='appinfo-body']")[0]
    app_name = header_el.xpath("./h3/text()")[0].strip()

    app_info_el = header_el.xpath("./div[@class='appinfo-info']")[0]
    app_author = app_info_el.xpath("./div[@class='appinfo-auther']")[0].xpath("./p[@class='content']/text()")[0]
    app_category = app_info_el.xpath("./div[@class='appinfo-category']")[0].xpath("./p/@title")[0]
    app_id = app_info_el.xpath("./div[@class='appinfo-auther qrcode-area']/p[@class='content']/a/text()")[0]
    app_price = app_info_el.xpath("./div[@class='appinfo-auther']")[1].xpath("./p[@class='content']/text()")[0]
    latest_version = app_info_el.xpath("./div[@class='appinfo-auther']")[2].xpath("./p[@class='content']/text()")[0].strip()

    base_info = info_dict.setdefault("baseinfo", {}).setdefault("info", {})
    base_info.update({"app_author": app_author,
                      "app_category": app_category,
                      "app_id": app_id,
                      "app_price": app_price,
                      "app_name": app_name,
                      "latest_version": latest_version})

    screen_el = el.xpath("//div[@id='container']")[0]
    pics_els = screen_el.xpath("./div[@class='aso100-nav-label screenimg']/a")
    
    pic_dict = {}
    for pic_el in pics_els:
        key = pic_el.xpath("./text()")[0]
        pic_images = pic_el.xpath("./@data-imgstr")[0].split(",")
        pic_dict[key] = pic_images

    # 处理应用截图
    base_info.update({"pic_dict": pic_dict})

    desc = screen_el.xpath("./div[@class='desc']")[0]
    desc = lxml.html.tostring(desc)
    baseinfo_content = screen_el.xpath("./table[@class='base-info base-area']")[0]
    baseinfo_content = lxml.html.tostring(baseinfo_content)

    # 处理相关产品
    ralation_apps = screen_el.xpath("./ul[@class='app-list-simple clearfix']/li")

    for app in ralation_apps:
        app_name = app.xpath("./a/p/text()")[0]
        app_logo = app.xpath("./a/img/@src")[0]

        app_dict = {"app_name": app_name,
                    "app_logo": app_logo}

        base_info.setdefault("ralation_apps", []).append(app_dict)

    base_info.update({"desc": desc, "baseinfo_content": baseinfo_content})


def process_version_info(browser, el, info_dict):
    """
    处理app历史版本信息的采集

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict

    :return:
    """
    version_els = el.xpath("//div[@id='container']/table/tbody/tr")

    for version_el in version_els:
        version = version_el.xpath("./td")[0].xpath("./text()")[0]
        update_time = version_el.xpath("./td")[1].xpath("./text()")[0]
        icon = version_el.xpath("./td")[2].xpath("./img/@src")[0]
        title = version_el.xpath("./td")[2].xpath("./text()")[0]
        update_desc = version_el.xpath("./td")[3]
        update_desc = lxml.html.tostring(update_desc)

        cur_version = {"version": version,
                       "update_time": update_time,
                       "icon": icon,
                       "title": title,
                       "update_desc": update_desc}

        info_dict.setdefault("version_info", []).append(cur_version)


def process_compete_info(browser, el, info_dict):
    """
    处理竞品页面的智能推荐

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict

    :return:
    """
    compet_els = el.xpath("//div[@id='container']/div[@class='competi-base ']/table/tbody/tr")

    for compet_el in compet_els:
        seq = compet_el.xpath("./td")[0].xpath("./text()")[0]
        app_logo = compet_el.xpath("./td")[1].xpath("./a/div[@class='media-left media-middle']/img/@src")[0]
        app_name = compet_el.xpath("./td")[1].xpath("./a/div[@class='media-body']/h4/text()")[0]
        app_author = compet_el.xpath("./td")[1].xpath("./a/div[@class='media-body']/div/text()")[0]
        total_rank = compet_el.xpath("./td")[2].xpath("./div[@class='rank']/text()")[0]
        pay_type = compet_el.xpath("./td")[2].xpath("./div[@class='brand']/text()")[0]
        cur_ver_rank = compet_el.xpath("./td[@class='reting mobile-hide']")[0].xpath("./p[@class='num']/text()")[0]
        total_ver_rank = compet_el.xpath("./td[@class='reting mobile-hide']")[1].xpath("./p[@class='num']/text()")[0]

        cur_version = {"seq": seq,
                       "app_logo": app_logo,
                       "app_name": app_name,
                       "app_author": app_author,
                       "pay_type": pay_type,
                       "cur_ver_rank": cur_ver_rank,
                       "total_ver_rank": total_ver_rank,
                       "total_rank": total_rank}

        info_dict.setdefault("competi_info", []).append(cur_version)


def process_comment_info(browser, el, info_dict):
    """
    处理评论统计页面

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict

    :return:
    """
    def _process_static_info(comment_el):
        """ 处理统计信息的采集 """
        title = comment_el.xpath("./div[@class='head']/text()")[0]
        rate = comment_el.xpath("./div[@class='reting-box']/div[@class='reting']/p[@class='num']/text()")[0]
        star = comment_el.xpath("./div[@class='reting-box']/div[@class='reting']/p[@class='star']/span/@style")[0]
        star = INT_RE.findall(star)[0]

        comment_count = comment_el.xpath("./div[@class='reting-box']/div[@class='reting']/p[@class='all']/text()")[0]

        rate_range = {}
        range_els = comment_el.xpath("./div[@class='reting-box']/ul[@class='rating-info']/li")
        for range_el in range_els:
            name = range_el.xpath("./span[@class='name']/text()")[0]
            counter = range_el.xpath("./span")[2].xpath("./text()")[0]

            rate_range[name] = counter

        d = {"title": title,
             "rate": rate,
             "star": star,
             "comment_count": comment_count,
             "rate_range": rate_range}

        return title, d


def process_aso_compare_info(browser, el, info_dict):
    """
    处理aso排名相关页面

    @param browser: 当前selenium的浏览器实例
    @type browser: webdriver.Firefox()

    @param el: 当前页面的el实例
    @type el: lxml.etree.HTML

    @param info_dict: 存储基本信息的dict
    @type info_dict: Dict

    :return:
    """
    url = el.xpath("//a[@class='btn btn-custom export-data']/@href")[0]
    url = BASE_URL + url

    browser.get(url)
    app_name = info_dict.get("baseinfo", {}).get("app_name")

    fname = generate_fname(app_name)
    keywords = extract_keywords_xlsx(app_name, fname)

    info_dict.setdefault("aso", {}).update({"keywords": keywords})


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
    import ipdb;ipdb.set_trace()
    url = el.xpath("//a[@class='btn btn-custom export-data']/@href")[0]
    url = BASE_URL + url

    browser.get(url)
    app_name = info_dict.get("baseinfo", {}).get("app_name")

    fname = generate_fname(app_name, "comment")
    keywords = extract_keywords_xlsx(app_name, fname)

    info_dict.setdefault("aso", {}).update({"keywords": keywords})


if __name__ == "__main__":
    parse_cates("")