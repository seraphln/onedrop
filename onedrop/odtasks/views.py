# coding=utf8
#


"""
onedrop首页相关接口
"""

from onedrop.utils import make_api_response

from onedrop.odtasks.funcs import update_ctasks


def update_crawler_task(request):
    """ 通过POST形式更新采集到的信息 """
    update_ctasks(request.POST.get("task_result"))
    return make_api_response({})