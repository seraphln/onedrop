# coding=utf-8
#


"""
excel文件的解析
"""

import xlrd


def extract_keywords_xlsx(appname, fname):
    """
        解析给定的excel文件

        @param fname: 给定的excel文件的文件名
        @type fname: String

        :return:
    """
    workbook = xlrd.open_workbook(fname)
    sheet_name = u"%s_关键词覆盖数据" % appname
    print sheet_name
    booksheet = workbook.sheet_by_name(sheet_name)

    row_data = []
    # 第一行开始是关键词数据
    for row in range(7, booksheet.nrows):

        keyword = booksheet.cell(row, 1).value
        rank = booksheet.cell(row, 2).value
        rank_change = booksheet.cell(row, 3).value
        figure = booksheet.cell(row, 4).value
        search_num = booksheet.cell(row, 5).value

        l = [keyword, rank, rank_change, figure, search_num]
        row_data.append(l)

    return row_data


if __name__ == "__main__":
    appname = u"拼多多"
    fname = u"/tmp/拼多多_关键词覆盖数据_20171027.xlsx"
    print extract_keywords_xlsx(appname, fname)