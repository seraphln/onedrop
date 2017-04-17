# coding=utf8
#


"""
onedrop首页相关接口
"""

from django.http import HttpResponse
from onedrop.utils import make_api_response

from onedrop.odtasks.funcs import update_ctasks

from onedrop.odtasks.models import CrawlerTasks

from onedrop.utils.excel import process_export_excel


def update_crawler_task(request):
    """
        通过POST形式更新采集到的信息
        之所以不用graphql是因为要传递原始页面回来，如果用graphql的话，会导致
        整个的结果太大，造成传递失败
    """
    update_ctasks(request.POST.get("task_result"))
    return make_api_response({})


def export_crawler_tasks(request):
    """
        按照任务ID，导出数据采集的结果
        导出结果包括：
            简历列表（名称、ID），简历第一次添加时更新时间、后续所有的更新时间
    """
    source = request.GET.get("source")
    crawler_tasks = CrawlerTasks.objects.filter(source=source)

    filename, tmp_file = process_export_excel(source, crawler_tasks)
    excel_data = tmp_file.getStream()
    tmp_file.close()
    response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % filename.encode('utf8')
    return response