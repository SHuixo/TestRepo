import random
import re
from lxml import etree
import scrapy
import copy
import csv
import time
import logging
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from scrapy.conf import settings
from selenium import webdriver
from WXReader.spiders import utils
from WXReader.items import WXItem


class WXSpider(scrapy.Spider):
    # 可按照之前的方案爬取数据！
    # 获取数据方式需结合反推!
    name = 'WXReader'
    allow_domains = ["weread.qq.com"]

    def __init__(self):
        # chrome浏览器设置！
        self.timeout = 30
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser_options.add_argument('lang=zh_CN.utf-8')
        self.headers = {"User-Agent": random.choice(settings["USER_AGENTS"])}
        self.types = [utils.TopType, utils.OtherType]
        self.url = "https://weread.qq.com/web/category/{ttype}" # 当 SWITCH 为 True 时使用！
        self.SWITCH = True   # 定义两种数据爬取方式 True调用selenium插件，False则通过url返回的json提取。

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
        item["app"] = "微信阅读"

        if self.SWITCH :
            # 通过下拉页面刷新！
            for flag, types in enumerate(self.types):
                for ttype in types:
                    self.headers = {"User-Agent": random.choice(settings["USER_AGENTS"])}
                    self.browser_options.add_argument('User-Agent={}'.format(self.headers))
                    driver = webdriver.Chrome(chrome_options=self.browser_options)
                    driver.get(url=self.url.format(ttype=ttype))
                    # 每一页页面的下拉次数
                    for _ in range(20):
                        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                        ActionChains(driver).key_up(Keys.UP).perform()
                        time.sleep(random.uniform(0.6,0.8)*10)

                    resHtml = driver.page_source
                    resEtree = etree.HTML(resHtml)
                    hrefs = resEtree.xpath(r'//*[@id="routerView"]/div[2]/ul/*/a/@href')
                    for href in hrefs:
                        url = "https://weread.qq.com"+href
                        response = scrapy.Request(url=url, meta=copy.deepcopy({"meta": item}), callback=self.getHtml)
                        yield response
        else:
            # 直接获取json数据！
            for flag, types in enumerate(self.types):
                for ttype in types:
                    logging.warning("开始执行 type -> {}".format(ttype))
                    for index in range(20):
                        logging.warning("开始执行 type -> {ttype} index ->{index}".format(ttype=ttype, index=index))
                        response = scrapy.Request(url=utils.urls[flag].format(type=ttype, index=index*20),
                                                  meta=copy.deepcopy({"meta": item}), callback=self.getJson)
                        yield response

    def getJson(self, response):
        # json格式的数据解析,存在部分字段信息缺失，优先以 getHtml 方法为主
        item = response.meta["meta"]
        resJson = str(response.text)
        if response.selector.re(r'"books":(.*?),') == ['[]']:
            yield None
        else:
            bookIds = response.selector.re(r'"bookId":"(.*?)",')
            titles = response.selector.re(r'"title":"(.*?)",')
            authors = response.selector.re(r'"author":"(.*?)",')
            scores = response.selector.re(r'"star":(.*?),')
            scores = [ (int (x))/10 for x in scores ]
            classifies = response.selector.re(r'"category":"(.*?)",')
            commNums = response.selector.re(r'"ratingCount":(.*?),')
            readNums = response.selector.re(r'"readingCount":(.*?),')

            for i in range(len(bookIds)):
                item["uid"] = bookIds[i]
                item["name"] = titles[i]
                item["author"] = authors[i]
                item["score"] = scores[i]
                item["classify"] = classifies[i]
                item["commNum"] = commNums[i]
                item["readNum"] = readNums[i]

                yield item

    def getHtml(self, response):
        # 从动态页面获取阅读所有信息，获取数据比较完整，以此为主!
        item = response.meta["meta"]
        pass
