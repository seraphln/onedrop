# coding=utf8
#


"""
解析微信页面需要用到的工具函数集合
"""

import json
import lxml.html
from urllib2 import urlparse

base_url = "http://weixin.sogou.com/"


def parse_user_info(el, txt):
    """
        解析用户信息

        @param el: 给定的用户信息的lxml节点
        @type el: lxml.etree.node

        :return: ({user_info}, content_lst, content_urls)
    """
    c_base_url = 'http://mp.weixin.qq.com'

    user_el = el.xpath("//div[@class='profile_info_area']")[0]

    ugroup_el = user_el.xpath("./div[@class='profile_info_group']")[0]
    user_img = ugroup_el.xpath("./span/img/@src")[0]
    user_name = ugroup_el.xpath("./div[@class='profile_info']/strong/text()")[0]
    user_wechatid = ugroup_el.xpath("./div[@class='profile_info']/p/text()")[0]
    user_wechatid = user_wechatid.replace(u"微信号:", "").strip()

    udesc_els = user_el.xpath("./ul[@class='profile_desc']/li")

    user_desc = udesc_els[0].xpath("./div[@class='profile_desc_value']/text()")[0]
    user_verify_info = udesc_els[1].xpath("./div[@class='profile_desc_value']/text()")[0]

    line = filter(lambda x: "var msgList" in x, txt.split("\n"))[0]
    data = json.loads(line.strip().replace("var msgList = ", "").replace(";", ""))

    content_lst = data.get("list")
    for content in content_lst:
        c = content["app_msg_ext_info"]
        c["content_url"] = c_base_url + c["content_url"]

    content_urls = []

    try:
        els = el.xpath("//div[@class='weui_msg_card_list']/div[@class='weui_msg_card']")
        for cel in els:
            c_url = cel.xpath("./div[@class='weui_msg_card_bd']/div/span/@hrefs")[0]
            content_urls.append(c_base_url + c_url)
    except:
        pass

    user_info = {'user_img': user_img,
                 'username': user_name,
                 'user_wechatid': user_wechatid,
                 'user_desc': user_desc,
                 'user_verify_info': user_verify_info}

    return user_info, content_lst, content_urls


def find_correct_element_url(name, el, search_resp):
    """
        根据给定的参数，找到正确的dom节点

        @param name: 需要采集的微信公众号名称
        @type name: String 

        @param el: 下载页面的lxml.etree的节点
        @type el: lxml.etree.node

        @param search_resp: 下载的页面
        @type search_resp: String

        :return: url
    """
    base_el = el.xpath("//div[@class='wrapper']/div[@class='main-left']")[0]
    els = base_el.xpath("./div[@class='news-box']/ul/li")
    print '---------------------------'
    print len(els)
    print '---------------------------'

    for c_el in els:
        t_el = c_el.xpath("./div[@class='gzh-box2']/div[@class='txt-box']")[0]
        nick_name = t_el.xpath("./p/a/em/text()")[0]
        print nick_name
        if name == nick_name:
            url = t_el.xpath("./p/a/@href")[0]
            return url
    else:
        print search_resp 

    return ""


def parse_page_content(el, txt):

    """ 解析正文页面，抓取对应的数据 """

    result = {}

    cel = el.xpath("//div[@id='page-content']")[0]
    
    title = cel.xpath("./div[@id='img-content']/h2/text()")[0].strip()

    mel = cel.xpath("./div[@id='img-content']/div[@class='rich_media_meta_list']")[0]
    try:
        is_origin = mel.xpath("./span[@id='copyright_logo']/text()")[0]
    except:
        is_origin = ""
    created_on = mel.xpath("./em[@id='post-date']/text()")[0]
    author = mel.xpath("./em[@class='rich_media_meta rich_media_meta_text'][2]/text()")[0]

    con_el = cel.xpath("./div[@id='img-content']/div[@class='rich_media_thumb_wrp']")[0]
    try:
        img = con_el.xpath("./img/@src")[0]
    except:
        img = ""

    con_el = cel.xpath("./div[@id='img-content']/div[@id='js_content']")[0]
    page_content = lxml.html.tostring(con_el)

    ex_el = cel.xpath("./div[@id='img-content']/div[@id='js_sg_bar']")[0]
    try:
        view_count = int(ex_el.xpath("./div[@class='media_tool_meta tips_global meta_primary']/span/span/text()")[0])
    except:
        view_count = 0
    try:
        like_count = int(ex_el.xpath("./span[@class='media_tool_meta meta_primary tips_global meta_praise']/span/span/text()")[0])
    except:
        like_count = 0

    comments = []
    cmts = cel.xpath("./div[@class='rich_media_area_extra']/div[@class='rich_media_extra']/div[@class='discuss_container']/ul[@class='discuss_list']/li")

    for cmt in comments:
        like_count = int(cmt.xpath("./div[@class='discuss_opr']/span/span/text()")[0])
        c_author = cmt.xpath("./div[@class='user_info']/strong/text()")[0]
        c_author_avatar = cmt.xpath("./div[@class='user_info']/img/@src")[0]
        cmt_content = cmt.xpath("./div[@class='discuss_message']/div[@class='discuss_message_content']/text()")[0]

        comments.append({"like_count": like_count,
                         "c_author": c_author,
                         "c_author_avatar": c_author_avatar,
                         "cmt_content": cmt_content})

    result.update({"title": title,
                   "is_origin": is_origin,
                   "created_on": created_on,
                   "author": author,
                   "content": page_content,
                   "img": img,
                   "view_count": view_count,
                   "like_count": like_count,
                   "comments": comments})

    return result
