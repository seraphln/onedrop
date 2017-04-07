# coding=utf8
#


"""
onedrop的odtasks模块的后台管理配置
"""


from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from onedrop.odtasks.models import CrawlerNodes
from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks


class CrawlerSeedsAdmin(admin.ModelAdmin):
    """ 爬虫种子后台管理页面 """
    list_display = ("id",
                    "name",
                    "url",
                    "user",
                    "status",
                    "created_on",
                    "modified_on",
                    "last_crawl_on")
    list_filter = ("status",
                   ("created_on", DateFieldListFilter),
                   ("modified_on", DateFieldListFilter),
                   ("last_crawl_on", DateFieldListFilter))
    search_fields = ("name", "url", "user")


class CrawlerTasksAdmin(admin.ModelAdmin):
    """ 爬虫任务后台管理页面 """
    list_display = ("id",
                    "ttype",
                    "url",
                    "status",
                    "last_crawl_on",
                    "created_on",
                    "modified_on")
    list_filter = ("status",
                   ("created_on", DateFieldListFilter),
                   ("modified_on", DateFieldListFilter),
                   ("last_crawl_on", DateFieldListFilter))
    search_fields = ("ttype", "url", "status", "source")


class CrawlerNodesAdmin(admin.ModelAdmin):
    """ 爬虫节点后台管理页面 """
    list_display = ("id",
                    "name",
                    "remote_addr",
                    "status",
                    "last_join_on",
                    "last_offline_one")
    list_filter = ("status",
                   "name",
                   ("last_join_on", DateFieldListFilter))
    search_fields = ("name", "remote_addr", "status")


admin.site.register(CrawlerSeeds, CrawlerSeedsAdmin)
admin.site.register(CrawlerTasks, CrawlerTasksAdmin)
admin.site.register(CrawlerNodes, CrawlerNodesAdmin)