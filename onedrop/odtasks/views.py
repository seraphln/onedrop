# coding=utf8
#


"""
onedrop首页相关接口
"""

from onedrop.utils import make_api_response

from onedrop.odtasks.funcs import update_ctasks


def update_crawler_task(request):
    """
        通过POST形式更新采集到的信息
        之所以不用graphql是因为要传递原始页面回来，如果用graphql的话，会导致
        整个的结果太大，造成传递失败
    """
    update_ctasks(request.POST.get("task_result"))
    return make_api_response({})