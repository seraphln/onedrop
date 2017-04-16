# coding=utf8
#


"""
解析微信页面需要用到的工具函数集合
"""

from urllib2 import urlparse

base_url = "http://weixin.sogou.com/"


def parse_user_info(el):
    """
        解析用户信息

        @param el: 给定的用户信息的lxml节点
        @type el: lxml.etree.node

        :return: ({user_info}, content_urls)
    """
    c_base_url = 'http://mp.weixin.com.cn/'

    user_el = el.xpath("//div[@class='profile_info_area']")[0]

    ugroup_el = user_el.xpath("./div[@class='profile_info_group']")[0]
    user_img = ugroup_el.xpath("./span/img/@src")[0]
    user_name = ugroup_el.xpath("./div[@class='profile_info']/strong/text()")[0]
    user_wechatid = ugroup_el.xpath("./div[@class='profile_info']/p/text()")[0]
    user_wechatid = user_wechatid.replace(u"微信号:", "").strip()

    udesc_els = user_el.xpath("./ul[@class='profile_desc']/li")

    user_desc = udesc_els[0].xpath("./div[@class='profile_desc_value']/text()")[0]
    user_verify_info = udesc_els[1].xpath("./div[@class='profile_desc_value']/text()")[0]

    content_urls = []

    content_els = el.xpath("//div[@class='weui_msg_card_list']/div[@class='weui_msg_card']")
    for ct_el in content_els:
        c_url = ct_el.xpath("./div[@class='weui_msg_card_bd']/div/span/@hrefs")[0]
        c_url = c_base_url + c_url

        content_urls.append(c_url)

    user_info = {'user_img': user_img,
                 'username': user_name,
                 'user_wechatid': user_wechatid,
                 'user_desc': user_desc,
                 'user_verify_info': user_verify_info}

    return user_info, content_urls


def find_correct_element_url(params, el, search_resp):
    """
        根据给定的参数，找到正确的dom节点

        @param params: 启动参数
        @type params: opt_args

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
        if params.name == nick_name.encode('utf8'):
            url = t_el.xpath("./p/a/@href")[0]
            return url
    else:
        print search_resp.text

    return ""

