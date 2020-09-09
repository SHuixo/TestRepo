import random
import re
from lxml import etree
import scrapy
import copy
import csv
import time
import logging
import json
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from scrapy.conf import settings
from selenium import webdriver
from WXReader.spiders import utils
from WXReader.items import WXItem
from scrapy.selector import Selector


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
        self.types = [utils.TopType,
                      utils.OtherType
                      ]
        self.url = "https://weread.qq.com/web/category/{ttype}" # 当 SWITCH 为 True 时使用！
        self.SWITCH = True #False #True   # 定义两种数据爬取方式 True调用selenium插件，False 则通过url返回的json提取。

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
                    logging.warning("开始执行 ttype -> {}".format(ttype))
                    self.headers = {"User-Agent": random.choice(settings["USER_AGENTS"])}
                    self.browser_options.add_argument('User-Agent={}'.format(self.headers))
                    driver = webdriver.Chrome(chrome_options=self.browser_options)
                    driver.get(url=self.url.format(ttype=ttype))
                    # 每一页页面的下拉次数
                    for _ in range(30):
                        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                        ActionChains(driver).key_up(Keys.UP).perform()
                        time.sleep(random.uniform(0.6,0.8)*10)
                    logging.warning("ttype -> {} 页面下拉刷新完毕！！".format(ttype))
                    resHtml = driver.page_source
                    resEtree = etree.HTML(resHtml)
                    hrefs = resEtree.xpath(r'//*[@id="routerView"]/div[2]/ul/*/a/@href')
                    driver.quit()
                    for href in hrefs:
                        url = "https://weread.qq.com"+href
                        response = scrapy.Request(url=url, meta=copy.deepcopy({"meta": item}), callback=self.getHtml)
                        yield response
                logging.warning("完成执行 types -> {}".format(types))
            logging.warning("完成执行 all types -> ")
        else:
            # 直接获取json数据！
            for flag, types in enumerate(self.types):
                for ttype in types:
                    logging.warning("开始执行 type -> {}".format(ttype))
                    for index in range(30):
                        logging.warning("开始执行 type -> {ttype} index ->{index}".format(ttype=ttype, index=index))
                        response = scrapy.Request(url=utils.urls[flag].format(type=ttype, index=index*20),
                                                  meta=copy.deepcopy({"meta": item}), callback=self.getJson)
                        yield response
                    logging.warning("完成执行 ttype -> {} 所有的index".format(ttype))
                logging.warning("完成执行 ttype -> {}".format(types))
            logging.warning("完成执行 all types -> ")

    def getJson(self, response):
        # json格式的数据解析,存在部分字段信息缺失，优先以 getHtml 方法为主
        item = response.meta["meta"]
        resJson = response.text
        if response.selector.re(r'"books":(.*?),') == ['[]']:
            yield None
        else:
            #通过正则获取数据！！
            # bookIds = response.selector.re(r'"bookId":"(.*?)",')
            # titles = response.selector.re(r'"title":"(.*?)",')
            # authors = response.selector.re(r'"author":"(.*?)",')
            # scores = response.selector.re(r'"star":(.*?),')
            # scores = [ (int (x))/10 for x in scores ]
            # classifies = response.selector.re(r'"category":"(.*?)",')
            # commNums = response.selector.re(r'"ratingCount":(.*?),')
            # readNums = response.selector.re(r'"readingCount":(.*?),')
            #
            # for i in range(len(bookIds)):
            #     item["uid"] = bookIds[i]
            #     item["name"] = titles[i]
            #     item["author"] = authors[i]
            #     item["score"] = scores[i]
            #     item["classify"] = classifies[i]
            #     item["type"] = classifies[i]
            #     item["commNum"] = commNums[i]
            #     item["readNum"] = readNums[i]
            #
            #     yield item

            #通过json方法获取
            infoJson = json.loads(resJson)
            books = infoJson.get('books')
            for book in books:
                item["uid"] = book.get('bookInfo').get('bookId')
                item["name"] = book.get('bookInfo').get('title')
                item["author"] = book.get('bookInfo').get('author')
                item["score"] = (int)(book.get('bookInfo').get('star'))/10
                item["classify"] = book.get('bookInfo').get('category')
                item["type"] = book.get('bookInfo').get('category')
                item["price"] = str(book.get('bookInfo').get('price'))+'￥'
                item["commNum"] = book.get('bookInfo').get('ratingCount')
                item["readNum"] = book.get('readingCount')

                yield item


    def getHtml(self, response):

        # 从动态页面获取阅读所有信息，获取数据比较完整，以此为主!
        item = response.meta["meta"]
        content = response.selector.re(r'"meta":{}}},"reader":(.*?)"chapterInfos":')[0]
        sel = Selector(text=content)
        item["uid"] = sel.re(r'"bookId":"(.*?)",', content)[0]
        S = sel.re(r'"category":"(.*?)",', content)
        if S != []:
            item["classify"] = S[0]
            item["type"] = S[0]
        item["author"] = sel.re(r'"author":"(.*?)",', content)[0]
        item["name"] = sel.re(r'"title":"(.*?)",', content)[0]
        item["publish"] = sel.re('"publisher":"(.*?)",', content)[0]
        item["ptime"] = sel.re(r'"publishTime":"(.*?)",', content)[0]
        S = sel.re(r'"publishPrice":(.*?),', content)
        if S != []:
            item["price"] =S[0]+'￥'
        item["isbn"] = sel.re(r'"isbn":"(.*?)",', content)[0]
        S = sel.re(r'"star":(.*?),', content)
        if S != []:
            item["score"] = ((int)(S[0]))/10
        S = sel.re(r'"ratingCount":(.*?),', content)
        if S != []:
            item["commNum"] = S[0]
        S = sel.re(r'"readingCount":(.*?)},', content)
        if S != []:
            item["readNum"] = S[0]

        yield item
