# coding=utf-8
#


""" main schema """


import graphene
import onedrop.odtasks.schema

from onedrop.odtasks.schema import types as odtask_types


class Query(onedrop.odtasks.schema.Query, graphene.ObjectType):
    pass


class Mutation(onedrop.odtasks.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, types=odtask_types)