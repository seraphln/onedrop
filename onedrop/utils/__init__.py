# coding=utf8
#


import json
from django.conf import settings

from django.http import HttpResponse
from django.shortcuts import render_to_response


def make_api_response(result=None, page_info=None, message=""):
    """
        构造api结构的返回
        结构大致如下:
            {success: True/False,
            message: error message,
            data: result,
            result_info: result_info}
    """
    ret = {"success": len(message) == 0,
           "errors": [],
           "message": message,
           "data": result}

    if page_info:
        ret.update({"page_info": page_info})

    resp = HttpResponse(json.dumps(ret), content_type="application/json")
    return resp


def smart_str(o):
    """ 格式化给定的字符串，如果给定的是unicode，那么转换成str """

    if isinstance(o, unicode):
        return o.encode('utf8')
    else:
        return o
