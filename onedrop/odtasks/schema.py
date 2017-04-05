# coding=utf-8
#


"""
onedrop项目下odtasks模块的graphql的schema集合
"""


import graphene
from graphene import relay
from graphene import AbstractType

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from onedrop.odtasks.models import CrawlerNodes as CrawlerNodesModel
from onedrop.odtasks.models import CrawlerSeeds as CrawlerSeedsModel
from onedrop.odtasks.models import CrawlerTasks as CrawlerTasksModel

from onedrop.odtasks.funcs import update_cnodes
from onedrop.odtasks.funcs import update_ctasks
from onedrop.odtasks.funcs import get_crawler_task

from onedrop.partner.utils import check_permission


class CrawlerNodes(DjangoObjectType):
    """ schema中的crawlerNodes对象 """

    class Meta:
        model = CrawlerNodesModel
        filter_fields = ["name", "status"]
        interfaces = (graphene.relay.Node, )


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
        filter_fields = ["category", "url", "ttype", "source"]
        interfaces = (graphene.relay.Node, )


class CrawlerTasksMutation(graphene.relay.ClientIDMutation):
    """ 基于ID的mutation对象 """

    class Input:
        task_result = graphene.String()

    ctask = graphene.Field(CrawlerTasks)

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        """ 处理mutate信息 """
        if not check_permission(context):
            return []

        task_result = input.get("task_result")
        ctask = update_ctasks(task_result)
        return CrawlerTasksMutation(ctask=ctask)


class CrawlerNodesMutation(graphene.relay.ClientIDMutation):
    """ 基于ID的nodes mutation对象 """

    class Input:
        node_info = graphene.String()

    cnode = graphene.Field(CrawlerNodes)

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        """ 处理mutate信息 """
        if not check_permission(context):
            return CrawlerNodesMutation(cnode=None)
        node_info = input.get("node_info")
        remote_addr = context.environ.get("REMOTE_ADDR")
        cnode = update_cnodes(node_info, remote_addr=remote_addr)

        return CrawlerNodesMutation(cnode=cnode)


class Query(AbstractType):
    """ odtasks app下的query结构 """
    crawler_seed = graphene.Field(CrawlerSeeds)
    crawler_seeds = relay.Node.Field(CrawlerSeeds)
    all_crawler_seeds = DjangoFilterConnectionField(CrawlerSeeds)

    crawler_task = graphene.Field(CrawlerTasks)
    crawler_tasks = relay.Node.Field(CrawlerTasks)
    all_crawler_tasks = DjangoFilterConnectionField(CrawlerTasks)

    #@graphene.resolve_only_args
    #def resolve_all_crawler_seeds(cls, **kwargs):
    def resolve_all_crawler_seeds(self, args, context, info):
        """ 解析crawler seed """
        if not check_permission(context):
            return []
        return get_crawler_task(queue="seed", source="seed")

    @graphene.resolve_only_args
    def resolve_all_crawler_tasks(cls, **kwargs):
        """ 解析mtask """
        if not check_permission(context):
            return []
        source = kwargs.get("source")
        if not source:
            return []
        else:
            return get_crawler_task(queue="task", source=source)


class Mutation(AbstractType):
    """ adtasks app下的mutation结构 """
    ctasks = CrawlerTasksMutation.Field()
    cnodes = CrawlerNodesMutation.Field()

types = [CrawlerSeeds, CrawlerTasks]
