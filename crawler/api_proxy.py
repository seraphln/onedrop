# coding=utf8
#


"""
跟远程API服务器交互的通用逻辑
"""

import os
import json
import socket
import urllib
import datetime
import requests
import traceback

import config


API_HOST = "http://180.76.149.212:8083"
GRAPHQL_HOST = "%s/graphql?query=%%s" % API_HOST


def to_url_params(params):
    """
        根据GET参数的请求对URL进行编码
        @param params: GET参数
        @type params: Dict

        :return: urllib.urlencode(params)
    """
    if not params:
        return ""
    new_params = {}
    for k,v in params.items():
         if isinstance(v, unicode):
             new_params[k] = v.encode('utf-8')
         elif isinstance(v, str):
             new_params[k] = v
         else:
             raise
    return urllib.urlencode(new_params)


def request(method, url, params=None):
    """
        封装起来的请求远程服务器的操作

        @param method: 请求的HTTP Method
        @type method: String

        @param url: 请求的PATH
        @type url: String

        @param params: 请求所带的参数
        @type params: Dict

        @param ak: 请求所带的access_Key
        @type ak: String

        :return: api_response
    """
    start_time = str(datetime.datetime.now())
    headers = {}
    headers['X-Auth-Access-Key'] = config.API_ACCESS_KEY

    query_dict = {"headers": headers,
                  "verify": False,
                  "timeout": 60}

    data = None if not params else params

    if method == 'GET' and params:
        url += '?' + to_url_params(params)
        data = None
    else:
        if data:
            query_dict["data"] = data
    status_code = 0
    try:
        resp = requests.request(method, url, **query_dict)
        status_code = resp.status_code
        resp = resp.json()
    except:
        resp = {'success':False, 'result':traceback.format_exc()}

    resp['status_code'] = status_code
    resp['time'] = resp.get('time', {})
    resp['time']['api_start'] = start_time
    resp['time']['api_end'] = str(datetime.datetime.now())

    return resp


def get_crawler_seed():
    """
        获取采集的种子

        :return: {"data": {"tasks": cseeds[0].get("node")}}
    """
    query_str = ''' query fetchCrawlerSeeds{allCrawlerSeeds(source: "pcbaby") {
                        edges {
                            node {
                                id,
                                name,
                                source,
                                url,
                                status
                            }
                        }
                    }}
                '''
    data = request("GET", GRAPHQL_HOST % query_str)
    cseeds = data.get("data", {}).get("allCrawlerSeeds", {}).get("edges", [{}])
    print cseeds
    if not cseeds or cseeds[0].get("status") == "finished":
        return {}
    else:
        return {"data": {"seeds": cseeds[0].get("node")}}


def get_crawler_task(source):
    """
        从anduin的远程服务请求一个监控任务

        @param source: 爬虫任务对应的来源
        @type source: String

        :return: {"data": {"tasks": ctasks[0].get("node")}}
    """
    query_str = ''' query fetchCrawlerTasks{allCrawlerTasks(source: "%s") {
                        edges {
                            node {
                                id,
                                name,
                                url,
                                status,
                                category,
                                ttype
                            }
                        }
                    }}
                '''
    query_str = query_str % source
    data = request("GET", GRAPHQL_HOST % query_str)
    ctasks = data.get("data", {}).get("allCrawlerTasks", {}).get("edges", [{}])
    if not ctasks or ctasks[0].get("status") == "finished":
        return {}
    else:
        return {"data": {"tasks": ctasks[0].get("node")}}


def update_crawler_task_by_rest_api(task_result):
    """
        通过post请求将接口数据更新到远程服务器
        @param task_result: 爬虫任务采集的结果
        @type task_result: Dict

        :return: {}
    """
    url = "%s/update_crawler_task/" % API_HOST
    data = {"task_result": task_result}
    return request("POST", url, params=data)


def register_crawler_node(task_result):
    """ 将当前爬虫节点注册到服务器上 """
    query_str = '''
    mutation MTMutation {
        cnodes(input: {nodeInfo: "%s"}) {
            cnode {
                id,
                name,
                remoteAddr,
                status
            }
        }
    }
    '''

    query_str = query_str % str(task_result)

    url = GRAPHQL_HOST % query_str
    return request("POST", url)


def update_crawler_task(task_result):
    """ 将数据更新到远程服务器上 """
    query_str = '''
    mutation MTMutation {
        ctasks(input: {taskResult: "%s"}) {
            ctask {
                id,
                status
            }
        }
    }
    '''

    query_str = query_str % str(task_result)
    url = GRAPHQL_HOST % query_str
    return request("POST", url)


if __name__ == "__main__":
    #import json
    #import base64
    #task_result = {"name": "%s-%s" % (socket.gethostname(), os.getpid())}
    #print register_crawler_node(base64.urlsafe_b64encode(json.dumps(task_result)))
    print get_crawler_seed()