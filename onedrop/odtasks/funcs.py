# coding=utf8
#


"""
数据库交互相关函数
从models文件中抽出来
"""


from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks



def create_crawler_task_detail(name,
                               ttype,
                               url,
                               parent_cate=None,
                               status="pending"):
    """ 根据给定的参数创建crawler结果 """
    now = timezone.now()
    ct, flag = CrawlerTaskDetail.objects.get_or_create(name=name,
                                                       ttype=ttype,
                                                       url=url,
                                                       parent_cate=parent_cate)
    # 新创建记录
    if flag:
        ct.created_on = now
        ct.modified_on = now
    else:
        ct.modified_on = now

    ct.status = status
    ct.save()

    return ct


def update_ctasks(result):
    """ 根据id来更新mtasks """
    now = timezone.now()
    try:
        data = json.loads(base64.urlsafe_b64decode(str(result)))
    except:
        data = {}

    url, name, cate, ttype = (data.get("url"),
                              data.get("name"),
                              data.get("cate"),
                              data.get("ttype"))

    if any([not url, not name, not cate, not ttype]):
        return None
    else:
        queue = settings.TASK_QUEUE_MAPPER.get(ttype)
        if not queue:
            return None

        ct, flag = CrawlerTaskDetail.objects.get_or_create(url=url,
                                                           name=name,
                                                           cate=cate)
        # 创建的记录
        if flag:
            ct.created_on = now
            ct.modified_on = now
            ct.status = "pending"
            rop.add_task_queue(queue, str(ct.id))
        else:
            if not data.get("content"):
                return None

            ct.status = "finished"
            ct.content = data.get("content")
            ct.last_crawl_on = now
            ct.modified_on = now

        ct.save()
        return ct
