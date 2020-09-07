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

        for index,  types in enumerate(self.types):
            for type in types:
                time.sleep(10)
                logging.warning("开始执行 type -> {}".format(type))
                yield scrapy.Request(url=utils.urls[index].format(type=type),callback=self.getHtml)

    def getHtml(self, response):

        item = WXItem()
        print(item)
        #resJson = response.text

        #pass

