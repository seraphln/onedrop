# coding=utf8
#


"""
处理导出excel相关逻辑
"""

import json
import xlwt
import base64
import datetime
from pyExcelerator import CompoundDoc

from django.conf import settings


def getXlsStream(stream):
    """ 返回一个binary stream(用于生成excel文件) """
    doc = CompoundDoc.XlsDoc()
    padding = '\x00' * (0x1000 - (len(stream) % 0x1000))
    doc.book_stream_len = len(stream) + len(padding)
    doc._XlsDoc__build_directory()
    doc._XlsDoc__build_sat()
    doc._XlsDoc__build_header()

    return reduce(lambda x, y:x+str(y),
                  [doc.header,
                   doc.packed_MSAT_1st,
                   stream,padding,
                   doc.packed_MSAT_2nd,
                   doc.packed_SAT,
                   doc.dir_stream])


class OutputWrapper(object):
    """ 输出文件excel """

    def __init__(self, file_name, screen_name):
        self.file_name = (file_name + screen_name).encode("gbk", "ignore")
        self.xlsfile = xlwt.Workbook()
        self.sheet_cnt = 1
        self.row_cnt = 0
        self.row_limit = 50000
        self.cell_maxsize = 60000
        self.screen_name = screen_name

        self.table = self.xlsfile.add_sheet(self.screen_name + str(self.sheet_cnt),
                                            cell_overwrite_ok=True)

    def close(self):
        """ 关闭文件 """
        print self.file_name + ".xls"
        self.xlsfile.save(self.file_name + ".xls")
        return self.file_name

    def getStream(self):
        """ 将文件内容转换成流格式 """
        return getXlsStream(self.xlsfile.get_biff_data())

    def write(self, pos, data):
        """ 按照位置，将数据写入到指定的行 """
        #写入excel
        cnt = pos
        for item in data:
            if isinstance(item, int):
                tmp_data = item
            elif isinstance(item, float):
                tmp_data = item
            elif isinstance(item, bool):
                tmp_data = item
            else:
                tmp_data = unicode(item).encode("gbk", "ignore").decode("gbk", "ignore")
                if len(tmp_data) > self.cell_maxsize:
                    tmp_data = tmp_data[:self.cell_maxsize]
            self.table.write(self.row_cnt, cnt, tmp_data)
            cnt += 1

        self.row_cnt += 1
        if self.row_cnt >= self.row_limit:
            self.row_cnt = 0
            self.sheet_cnt += 1
            self.table = self.xlsfile.add_sheet(self.screen_name + str(self.sheet_cnt))

    def add_new_sheet(self):
        """ 添加一个新的sheet表单 """
        self.table = self.xlsfile.add_sheet(self.screen_name+str(self.sheet_cnt))


def process_pcbaby_export(tmp_file, ctasks):
    """ 处理pcbaby的导出任务 """
    for ctask in ctasks:
        value_lst = [ctask.parent_category,
                     ctask.category,
                     ctask.source,
                     ctask.url,
                     ctask.name,
                     ctask.content]
        tmp_file.write(0, value_lst)

    return tmp_file


def process_xindebaby_export(tmp_file, ctasks):
    """ 处理xindebaby的导出任务 """
    for ctask in ctasks:
        result = eval(ctask.result)
        capability = ""
        capability_dct = result.get("capability", {})
        capability += "disable: %s;" % ",".join(capability_dct.get("disable", []))
        capability += "enable: %s;" % ",".join(capability_dct.get("enable", []))

        doctor_lst = result.get("doctors", [])
        doctors = ""

        for doctor in doctor_lst:
            doctors += "avatar: %s, name: %s;" % (doctor.get("avatar", ""), doctor.get("name"))

        expense_lst = result.get("expense", [])
        expense = ""
        for cur_expense in expense_lst:
            expense += "%s;" % ",".join(cur_expense)

        process_lst = result.get("jiandang_process", [])
        jiandang_process = ""
        for process in process_lst:
            jiandang_process += "%s;" % ",".join(process)

        value_lst = [ctask.parent_category,
                     ctask.category,
                     ctask.source,
                     ctask.url,
                     ctask.name,
                     ",".join(result.get("tags")),
                     result.get("desc"),
                     result.get("address"),
                     result.get("avatar"),
                     capability,
                     doctors,
                     expense,
                     jiandang_process,
                     result.get("jiandang_status")]
        tmp_file.write(0, value_lst)

    return tmp_file


def process_export_excel(source, ctasks):
    """ 将采集任务的执行结果按照excel的格式导出出来 """
    now = datetime.datetime.now()
    tmp_name = u"%s_%s%s%s" % (source, now.year, now.month, now.day)
    tmp_file = OutputWrapper(settings.EXCEL_DIR, tmp_name)
    tmp_file.write(0, settings.EXPORT_COLUMN.get(source))

    process_mapper = {"pcbaby": process_pcbaby_export,
                      "xindebaby": process_xindebaby_export}

    return tmp_name, process_mapper[source](tmp_file, ctasks)

