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
from QQReader.spiders import utils
from QQReader.items import QQItem
from scrapy.selector import Selector


class WXSpider(scrapy.Spider):
    # 可按照之前的方案爬取数据！
    # 获取数据方式需结合反推!
    name = 'QQReader'
    #allow_domains = ["weread.qq.com"]

    def __init__(self):
        # chrome浏览器设置！
        self.timeout = 30
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser_options.add_argument('lang=zh_CN.utf-8')
        self.headers = {"User-Agent": random.choice(settings["USER_AGENTS"])}
        self.types = [utils.csBooks,
                      utils.qqBooks,
                      utils.qqRanks,
                      utils.YQBooks
                      ]

        self.SWITCH = True #False #True   # 定义两种数据爬取方式 True 默认采用的方式，False 则通过反推等手段！。


    def start_requests(self):

        item = QQItem()
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
        item["app"] = "QQ阅读"

        if self.SWITCH:
            for book in utils.csBooks:
                logging.warning("utils.csBooks book id 是-> {} ！！".format(book))
                for tag in utils.tags:
                    logging.warning("utils.tags tag id 是 -> {} ！！".format(tag))
                    url = book.format(tag=tag)
                    logging.warning("url -> {} 页面下拉刷新完毕！！".format(url))
                    response = scrapy.Request(url=url, meta=copy.deepcopy({"meta": item}), callback=self.getCsHtml)
                    yield response
                    logging.warning("请求完url = {} 的页面！！".format(url))
                logging.warning("utils.tag 请求完毕！！")
            logging.warning("utils.csBooks 请求完毕！！")

            for book in utils.qqBooks:
                logging.warning("utils.qqBooks book id 是-> {} ！！".format(book))
                #进行多页查询！(最多10页内容)
                for i in range(1,11):
                    nstr = '/'+ str(i) +'.html'
                    book = str(book).replace('/1.html',nstr)
                response = scrapy.Request(url=book, meta=copy.deepcopy({"meta": item}), callback=self.getqqBHtml)
                yield response
            logging.warning("utils.qqBooks 请求完毕！！")

            for book in utils.qqRanks:
                logging.warning("utils.qqRanks book id 是-> {} ！！".format(book))
                for i in range(1,11):
                    nstr = '&p='+ str(i)
                    book = str(book).replace('&p=1',nstr)
                    response = scrapy.Request(url=book, meta=copy.deepcopy({"meta": item}), callback=self.getqqRHtml)
                    yield response
            logging.warning("utils.qqRanks 请求完毕！！")

            for book in utils.YQBooks:
                if "yunqi.qq.com" not in book:
                    url = "http://yunqi.qq.com" + book
                else:
                    url = book
                logging.warning("utils.YQBooks book id 是-> {} ！！".format(book))
                response = scrapy.Request(url=url, meta=copy.deepcopy({"meta": item}), callback=self.getYQHtml)
                yield response
            logging.warning("utils.qqRanks 请求完毕！！")
        logging.warning("All utils 请求完毕！！")

    #创世书库
    def getCsHtml(self, response):
        item = response.meta["meta"]
        #获取当前页面所有的书名
        hrefs = response.xpath('/html/body/div[3]/div[4]/div[1]/table/tbody/tr[*]/td[3]/a[1]/@href').extract()
        names = response.xpath('string(/html/body/div[3]/div[4]/div[1]/table/tbody/tr[*]/td[3]/a[1])').extract_first()
        types = response.xpath('string(/html/body/div[3]/div[4]/div[1]/table/tbody/tr[*]/td[2]/a)').extract_first()
        authors = response.xpath('string(/html/body/div[3]/div[4]/div[1]/table/tbody/tr[*]/td[5]/a)').extract_first()
        ptimes = response.xpath('string(/html/body/div[3]/div[4]/div[1]/table/tbody/tr[*]/td[6]/span)').extract_first()

        for index, href in enumerate(hrefs):
            item["uid"] = str(href[:-5]).split("/")[-1]
            item["name"] = names[index]
            item["classify"] = types[index]
            item["type"] = types[index][1:-1]
            item["author"] = authors[index]
            item["ptime"] = ptimes[index]

            response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getCsItem)
            yield response

    #创世书库2
    def getCsItem(self, response):
        item = response.meta["meta"]
        item["label"] = str(response.xpath('string(/html/body/div[4]/div[3]/div[2]/div[1]/div[6])').extract_first()).split("：")[-1]

        yield item

    #qq阅读
    def getqqBHtml(self, response):
        item = response.meta["meta"]

        hrefs = response.xpath('//*[@id="bookListContainerByDetail"]/ul[*]/li[*]/div[2]/h3/a/@href').extract()
        names = response.xpath('//*[@id="bookListContainerByDetail"]/ul[*]/li[*]/div[2]/h3/a/@title').extract()
        authors = response.xpath('//*[@id="bookListContainerByDetail"]/ul[*]/li[*]/div[2]/h4/a/@title').extract()
        #//*[@id="bookListContainerByDetail"]/ul[*]/li[*]/div[2]/h4/a/@title

        for index, href in enumerate(hrefs):
            item["uid"] = str(href).split("bid=")[-1]
            item["name"] = names[index]
            item["author"] = authors[index]

            response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getqqBItem)
            yield response

    def getqqBItem(self, response):

        item = response.meta["meta"]
        item["publish"] = response.xpath('string(//*[@id="bookinfo"]/div[2]/dl[2]/dd[1])').extract_first()
        item["classify"] = response.xpath('string(//*[@id="bookinfo"]/div[2]/dl[1]/dd[2]/a)').extract_first()
        item["type"] = response.xpath('string(//*[@id="bookinfo"]/div[2]/dl[1]/dd[2]/a)').extract_first()
        item["price"] = response.xpath('string(//*[@id="bookinfo"]/div[2]/dl[2]/dd[3])').extract_first()

        yield item

    def getqqRHtml(self,response):
        item = response.meta["meta"]
        content = response.xpath('//*[@id="bookListByImg"]/div[1]/div/h3/a0').extract_first()
        if content is None:
            yield None
        else:
            hrefs = response.xpath('//*[@id="bookListByImg"]/div[*]/div/h3/a/@href').extract()
            names = response.xpath('//*[@id="bookListByImg"]/div[*]/div/h3/a/@title').extract()
            authors = response.xpath('string(//*[@id="bookListByImg"]/div[*]/div/dl[1]/dd[1]/a)').extract_first()
            types = response.xpath('string(//*[@id="bookListByImg"]/div[*]/div/dl[1]/dd[2]/a)').extract_first()
            publishs = response.xpath('string(//*[@id="bookListByImg"]/div[*]/div/dl[2]/dd[1])').extract_first()

            for index, href in enumerate(hrefs):
                item["uid"] = str(href).split("bid=")[-1]
                item["name"] = names[index]
                item["author"] = authors[index]
                item["classify"] = types[index]
                item["publish"] = publishs[index]

                response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getqqRItem)
                yield response

    def getqqRItem(self, response):

        item = response.meta["meta"]
        #获取分数 -- //*[@id="StarIcoValue"]/b/font
        item["score"] = response.xpath('string(//*[@id="StarIcoValue"]/b/font)').extract_first()
        item["type"] = response.xpath('string(//*[@id="bookinfo"]/div[2]/dl[1]/dd[2]/a)').extract_first()
        item["collNum"] = response.xpath('string(//*[@id="favorCount"])').extract_first()
        item["readNum"] = response.xpath('string(//*[@id="favorCount"])').extract_first()
        item["commNum"] = response.xpath('string(//*[@id="recommendCount"])').extract_first()

        yield item

    def getYQHtml(self, response):

        item = response.meta["meta"]
        resText = response.text

        titles = response.xpath('//*[@id="BookListDiv"]/*/a/@title').extract()
        hrefs = response.xpath('//*[@id="BookListDiv"]/*/a/@href').extract()
        authors = response.xpath('string(//*[@id="BookListDiv"]/*/div/dl[1]/dd[1]/a)').extract_first()
        types = response.xpath('string(//*[@id="BookListDiv"]/*/div/dl[1]/dd[2]/a)').extract_first()
        ptimes = response.xpath('string(//*[@id="BookListDiv"]/*/div/dl[2]/dd[1])').extract_first()

        for index, href in enumerate(hrefs):

            item["author"] = authors[index]
            item["classify"] = types[index]
            item["type"] = types[index]
            item["name"] = titles[index]
            item["ptime"] = ptimes[index]

            if '/bk/' in href:
                item["uid"] = str(href).split("/")[-1].split(".")[0]
                response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getYQItem)
                yield response
            else:
                item["uid"] = str(href).split("bid=")[-1]
                response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getYQItemO)
                yield response

    def getYQItem(self, response):
        item = response.meta["meta"]
        resText = response.text
        # 作品标签：
        #   宠文、总裁、杀伐果断、美食、豪门
        item["label"] = str(response.xpath(r'string(/html/body/div[3]/div[2]/div[2]/div[1]/div[6])').extract_first()).split('：')[-1]

        yield  item

    def getYQItemO(self, response):

        item = response.meta["meta"]
        resText = response.text
        #//*[@id="bookinfo"]/div[2]/dl[1]/dd[3]
        item["type"] = response.xpath('string(//*[@id="bookinfo"]/div[2]/dl[1]/dd[3])').extract_first()
        # //*[@id="favorCount"]
        # //*[@id="recommendCount"]
        item["commNum"] = response.xpath('string(//*[@id="recommendCount"])').extract_first()
        item["readNum"] = response.xpath('string(//*[@id="recommendCount"])').extract_first()
        item["collNum"] = response.xpath('string(//*[@id="favorCount"])').extract_first()
        # //*[@id="StarIcoValue"]/b/font
        item["score"] = response.xpath('string(//*[@id="StarIcoValue"]/b/font)').extract_first()

        yield item

    def start_requests2wx(self):

        item = QQItem()
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
        item["app"] = "QQ阅读"

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

    def getJson2wx(self, response):
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

    def getHtml2wx(self, response):

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
