import re

import scrapy
import copy
import csv
import time
import logging
from selenium import webdriver
from WXReader.spiders import utils
from WXReader.items import WXItem


class WXSpider(scrapy.Spider):
    #可按照之前的方案爬取数据！
    #获取数据方式需结合反推!
    name = 'WXReader'
    allow_domains = ["weread.qq.com"]

    def __init__(self):
        #chrome浏览器设置！
        self.timeout = 30
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser_options.add_argument('lang=zh_CN.utf-8')
        self.types = [utils.TopType, utils.OtherType]


    def start_requests(self):

        item = WXItem()
        item["uid"] = None
        item["classify"] = None
        item["type"] = None
        item["name"] = None
        item["author"] = None
        item["publish"] = None
        item["ptime"] = None
        item["price"] = None
        item["isbn"] = None
        item["country"] = None
        item["label"] = None
        item["score"] = None
        item["commNum"] = None
        item["readNum"] = None
        item["collNum"] = None
        item["app"] = None

        for flag, types in enumerate(self.types):
            for ttype in types:
                logging.warning("开始执行 type -> {}".format(ttype))
                for index in range(20):
                    logging.warning("开始执行 type -> {ttype} index ->{index}".format(ttype=ttype, index=index))
                    response = scrapy.Request(url=utils.urls[flag].format(type=ttype,index=index*20),callback=self.getHtml)
                    yield response

    def getHtml(self, response):

        resJson = str(response.text)
        if response.selector.re(r'"books":(.*?),') == ['[]']:
            yield None
        else:
            print(response.selector.re(r'"star":(.*?),'))
            # print(resJson)
            bookIds = re.findall(r'"bookId":"(.*?)",',resJson)
            titles = re.findall(r'"title":"(.*?)",',resJson)
            authors = re.findall(r'"author":"(.*?)",',resJson)
            #r'"star":(.*?),',
            scores = re.findall(r'"star":(.*?),',resJson,re.M|re.S)

            # scores = [x/10 for x in scores]
            classifies = re.findall(r'"category":"(.*?)",',resJson)
            commNums = re.findall(r'"ratingCount":(.*?),',resJson)
            readNums = re.findall(r'"readingCount":(.*?),',resJson)
            #pass
            # print(scores)

