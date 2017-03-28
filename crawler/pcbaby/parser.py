# coding=utf8
#


"""
pcbaby对应的parser实现
"""

import lxml.etree

from http import download_page


def parse_cates(cate, url, html):
    """
        解析分类以及对应的子分类信息

        @param cate: 当前分类的名称
        @type cate: String

        @param url: 当前分类对应的url
        @type url: String

        @param html: 当前url对应的页面信息
        @type html: String
    """

    result = {}

    el = lxml.etree.HTML(html)
    cates = el.xpath("//div[@class='baike-th']")
    sub_cates = el.xpath("//div[@class='baike-tb clearfix']")

    print "Starting to crawl cates with length: %s" % len(cates)
    for i, cate in enumerate(cates):
        print "Starting to crawl cate: %s, %s of %s" % (cate, i, len(cates))
        cate_name = cate.xpath("./div[@class='baike-th-name']/text()")[0]
        cate_dict = result.setdefault(cate_name, {})

        sub_cate = sub_cates[i]
        sub_cate_name = sub_cate.xpath("./div[@class='baike-tb-dl']/dl/dt/a/text()")[0]
        sub_cate_url = sub_cate.xpath("./div[@class='baike-tb-dl']/dl/dt/a/@href")[0]

        sub_dict = cate_dict.setdefault(sub_cate_name, {})
        sub_dict.update({"name": sub_cate_name, "url": sub_cate_url})

        third_cates = sub_cate.xpath("./div[@class='baike-tb-dl']/dl/dd/span")
        for i, third_cate in enumerate(third_cates):
            print "Starting to crawl third_cate: %s, %s of %s" % (third_cate, i, len(third_cates))
            third_cate_name = third_cate.xpath("./a/text()")[0]
            third_cate_url = third_cate.xpath("./a/@href")[0]

            sub_dict.setdefault(third_cate_name, {}).update({"name": third_cate_name,
                                                             "url": third_cate_url})

            # 获取url，并采集url对应页面信息
            try:
                resp = download_page(third_cate_url)
                content, cur_result = parse_detail_page(resp.text)
            except:
                content, cur_result = "", {}

            print "Done of crawl third_cate: %s, %s of %s" % (third_cate, i, len(third_cates))
            sub_dict.setdefault(third_cate_name, {}).update({"content": content,
                                                             "result": cur_result})

        print "Cate: %s, %s of %s" % (cate, i, len(cates))
    print "Done of crawl cates with length: %s" % len(cates)
    return result


def parse_detail_page(html):
    """ 解析详细的html页面，采集正文信息 """
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

    return content, result




if __name__ == "__main__":
    html = ""
    parse_cates("", "", html)