# coding=utf8
#


"""
数据采集任务管理相关数据模型集合
"""


from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from onedrop.odauth.models import OdUser


class CrawlerSeeds(models.Model):
    """ 数据采集任务的种子管理 """
    name = models.CharField(max_length=128, verbose_name=u"爬虫种子的名字")
    source = models.CharField(max_length=128, verbose_name=u"爬虫种子来源")
    url = models.CharField(max_length=255, verbose_name=u"种子的URL")
    user = models.ForeignKey(OdUser, verbose_name=u"爬虫种子创建人")
    status = models.CharField(max_length=32, verbose_name=u"爬虫种子状态")
    last_crawl_on = models.DateTimeField(default=timezone.now,
                                         verbose_name=u"上一次抓取时间")
    created_on = models.DateTimeField(default=timezone.now,
                                      verbose_name=u"爬虫种子创建时间")
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=u"爬虫种子修改时间")

    def is_crawling(self):
        """ 检查当前爬虫种子是否在爬取中 """
        return True if self.status == "crawling" else False

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"爬虫种子管理"
        verbose_name_plural = u"爬虫种子管理"


class CrawlerTasks(models.Model):
    """ 数据采集任务对应的URL以及管理结果 """
    url = models.CharField(max_length=255, verbose_name=u"需要采集的URL")
    name = models.CharField(max_length=128, verbose_name=u"当前采集任务的主题")
    # node, leaf
    ttype = models.CharField(max_length=32, verbose_name=u"当前任务的类型")
    source = models.CharField(max_length=32, verbose_name=u"任务来源", default="pcbaby")
    status = models.CharField(max_length=32,
                              default="pending",
                              verbose_name=u"数据采集任务的执行结果")
    content = models.TextField(default="",
                               blank=True,
                               null=True,
                               verbose_name=u"采集结果")
    result = models.TextField(default="",
                              blank=True,
                              null=True,
                              verbose_name=u"采集回来的原始结果")
    page = models.TextField(default="",
                            blank=True,
                            null=True,
                            verbose_name=u"原始页面")
    category = models.CharField(max_length=128,
                                null=True,
                                blank=True,
                                verbose_name=u"当前采集任务对应的分类")
    parent_category = models.CharField(max_length=128,
                                       null=True,
                                       blank=True,
                                       verbose_name=u"父分类")
    last_crawl_on = models.DateTimeField(default=timezone.now,
                                         verbose_name=u"上一次抓取时间")
    created_on = models.DateTimeField(default=timezone.now,
                                      verbose_name=u"种子创建时间")
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=u"种子修改时间")

    def __unicode__(self):
        return self.name

    def is_crawling(self):
        """ 检查当前种子是否在爬取中 """
        return True if self.status == "crawling" else False

    class Meta:
        verbose_name = u"数据采集URL管理"
        verbose_name_plural = u"数据采集URL管理"


class CrawlerNodes(models.Model):
    """ 爬虫节点注册模块 """
    name = models.CharField(max_length=255, verbose_name=u"爬虫节点的名称")
    remote_addr = models.CharField(max_length=255, verbose_name=u"爬虫节点IP")
    status = models.CharField(max_length=32, verbose_name=u"爬虫节点状态")
    last_join_on = models.DateTimeField(default=timezone.now,
                                        verbose_name=u"节点上线时间")
    last_offline_one = models.DateTimeField(default=timezone.now,
                                            verbose_name=u"节点下线时间")

    def __unicode__(self):
        return self.name

    def is_online(self):
        """ 检查当前爬虫节点是否在线 """
        return True if self.status == "online" else False

    class Meta:
        verbose_name = u"爬虫节点管理"
        verbose_name_plural = u"爬虫节点管理"
