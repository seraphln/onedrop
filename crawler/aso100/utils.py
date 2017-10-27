# coding=utf-8
#


"""
aso100爬虫相关的功能函数集合
"""

from datetime import datetime


def generate_fname(appname, ttype="keyword"):
    """
    生成文件名

    @param appname: 给定的应用名
    @type appname: String

    @param ttype: 文件类型
    @type ttype: String

    :return:
    """
    now = datetime.now()
    name_mapper = {"keyword": u"关键词覆盖数据",
                   "comment": u""}

    fname = "/tmp/%s_%s_%s.xlsx" % (appname,
                                    name_mapper[ttype],
                                    now.strftime("%Y%m%d"))

    return fname
