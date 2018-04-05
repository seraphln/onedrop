# coding=utf-8
#

import json
import requests


API_HOST = "180.76.53.122"
API_PORT = 8085

ACCESS_KEY = "8deea96fe5834e98b0d142d08617e336"


def get_task():
    """

    """
    url = "http://%s:%s/api/tasks/?access_key=%s" % (API_HOST, API_PORT, ACCESS_KEY)
    resp = requests.get(url)

    try:
        return json.loads(resp.text).get("data", {})
    except:
        return {}


def update_task(task):
    """

    """
    url = "http://%s:%s/api/tasks/%s/?access_key=%s" % (API_HOST, API_PORT, task.get("id"), ACCESS_KEY)
    resp = requests.put(url, data=json.dumps(task))

    if not resp.status_code == 200:
        print resp.text

    print resp.text



if __name__ == "__main__":
    get_task()
    #task = {"status": "finished", "data": {}, "id": 1, "keyword": "\u5f69\u94a2\u677f", "day": 7}
    #update_task(task)
