# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html


import sys
sys.path.append("/home/xianwu1/crawler/jd/jd")
import db
import random
from .useragents import agents
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class UserAgentmiddleware(UserAgentMiddleware):

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class ProxyMiddleware1(object):

    def __init__(self):
        # super(ProxyMiddleware1, self).__init__(settings)继承这里的坑以后再填吧
        #HttpProxyMiddleware.__init__(self, settings)
        '''类的重载这里我暂时调不好，老是报错，所以只好继承object了'''
        # self.ip_pools = [
        #     {'ip': '110.73.15.11:8123'},
        #     {'ip': '124.88.67.14:80'},
        #     {'ip': '42.81.58.198:80'},
        #     ]
        self.conn = db.RedisClient()

    def process_request(self, request, spider):
        ip = result = self.conn.random()
        print('当前使用的ip：',ip)
        #request.meta['proxy'] = 'http://{}'.format(ip['ip'])
        request.meta['proxy'] = 'http://{}'.format(ip)