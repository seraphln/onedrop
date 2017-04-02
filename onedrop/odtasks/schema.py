# coding=utf-8
#


"""
onedrop项目下odtasks模块的graphql的schema集合
"""


import graphene
from graphene import relay
from graphene import AbstractType

from django.conf import settings

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from onedrop.odtasks.models import CrawlerSeeds as CrawlerSeedsModel
from onedrop.odtasks.models import CrawlerTasks as CrawlerTasksModel

from onedrop.odtasks.views import get_crawl_task
from onedrop.odtasks.models import update_ctasks


class CrawlerSeeds(DjangoObjectType):
    """ schema中的crawlerSeeds对象 """

    class Meta:
        model = CrawlerSeedsModel
        filter_fields = ["name", "source"]
        interfaces = (graphene.relay.Node, )


class CrawlerTasks(DjangoObjectType):
    """ schema中的CrawlerTaskDetail对象 """

    class Meta:
        model = CrawlerTasksModel
        filter_fields = ["name", "url", "ttype"]
        interfaces = (graphene.relay.Node, )


class CrawlerTasksMutation(graphene.relay.ClientIDMutation):
    """ 基于ID的mutation对象 """

    class Input:
        task_result = graphene.String()

    ctask = graphene.Field(CrawlerTasks)

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        """ 处理mutate信息 """
        task_result = input.get("task_result")

        ctask = update_ctasks(task_result)
        return CrawlerTasksMutation(ctask=ctask)


class Query(AbstractType):
    """ odtasks app下的query结构 """
    crawler_seed = graphene.Field(CrawlerSeeds)
    crawler_seeds = relay.Node.Field(CrawlerSeeds)
    all_crawler_seeds = DjangoFilterConnectionField(CrawlerSeeds)

    crawler_task = graphene.Field(CrawlerTasks)
    crawler_tasks = relay.Node.Field(CrawlerTasks)
    all_crawler_tasks = DjangoFilterConnectionField(CrawlerTasks)

    @graphene.resolve_only_args
    def resolve_crawler_seed(cls, **kwargs):
        """ 获取一个爬虫种子 """
        return get_crawl_task("seed")

    @graphene.resolve_only_args
    def resolve_crawler_task(cls, **kwargs):
        """ 获取一个采集任务 """
        return get_crawl_task("seed")

    @graphene.resolve_only_args
    def resolve_all_crawler_tasks(cls, **kwargs):
        """ 解析mtask """
        source = settings.QUEUE_MAPPER.get(kwargs.get("source"))
        if not source:
            return []
        else:
            return get_crawl_task(source=source)


class Mutation(AbstractType):
    """ adtasks app下的mutation结构 """
    ctasks = CrawlerTasksMutation.Field()

types = [CrawlerSeeds, CrawlerTasks]
