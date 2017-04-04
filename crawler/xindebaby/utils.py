# coding=utf8
# 

import json
import base64
import requests


API_HOST = "http://180.76.149.212:8083/graphql?query=%s"


def get_crawler_task():
    """
        从anduin的远程服务请求一个监控任务
    """
    query_str = ''' query fetchCrawlerTasks{allCrawlerTasks(source: "xindebaby") {
                        edges {
                            node {
                                id,
                                name,
                                url,
                                status,
                                category,
                                source,
                                ttype
                            }
                        }
                    }}
                '''
    path = API_HOST % query_str
    resp = requests.get(path)
    data = json.loads(resp.text)
    cseeds = data.get("data", {}).get("allCrawlerTasks", {}).get("edges", [{}])
    if not cseeds or cseeds[0].get("status") == "finished":
        return {}
    else:
        return {"data": {"tasks": cseeds[0].get("node")}}


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

    path = API_HOST % query_str
    resp = requests.post(path)
    return json.loads(resp.text)


def update_crawler_task_by_rest_api(task_result):
    """ 通过post请求将接口数据更新到远程服务器 """
    path = "http://180.76.149.212:8083/update_crawler_task/"
    data = {"task_result": task_result}
    resp = requests.post(path, data=data)
    return json.loads(resp.text)


if __name__ == "__main__":
    #params = {"name": u"断奶奶涨怎么办",
    #          "parent_category": u"催乳回奶",
    #          "category": "断奶后回奶",
    #          "url": "http://baike.pcbaby.com.cn/qzbd/1269996.html",
    #          "ttype": "leaf"}
    #print update_crawler_task(base64.urlsafe_b64encode(json.dumps(params)))
    print get_crawler_task()