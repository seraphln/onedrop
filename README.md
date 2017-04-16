## OneDrop

### Intro
OneDrop是一个基于HTTP的分布式爬虫系统。
所有的采集任务通过中心服务进行管理。

所有的爬虫节点使用HTTP跟中心服务进行沟通。包括：
1. 爬虫注册
2. 任务获取
3. 任务结果回传

系统框架：
Django + GraphQL(graphene，服务端查询语言，graphene是GraphQL的Python实现) + Gevent(爬虫)

消息队列：
Redis，目前会根据不同的任务类型分配到不同的redis队列中。
这个部分需要在onedrop/settings.py中进行配置。

异步任务：
Celery
使用Django-Celery来记录一些异步任务的执行状态，而不是直接使用crontab。方便对任务进行管理。

持久化:
Sqlite3
可配置，在onedrop/settings.py配置需要的存储引擎即可。


### Demo
Admin: http://180.76.149.212:8083/admin


### TODO
