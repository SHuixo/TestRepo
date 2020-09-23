import copy
import random

import scrapy
from scrapy.conf import settings
from selenium import webdriver
from MIGUReader.spiders import utils
from MIGUReader.items import MGItem


class MGSpider(scrapy.Spider):
    ##必须将selenium包装成移动端设备，才可获取数据！
    #此脚本尝试pc端解析，不需要配合selenium！！
    name = 'MGReaderPC'

    def __init__(self):
        # chrome浏览器设置！
        self.timeout = 30
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser_options.add_argument('lang=zh_CN.utf-8')
        self.headers = {"User-Agent": random.choice(settings["USER_AGENTS"])}
        self.url = "https://weread.qq.com/web/category/{ttype}" # 当 SWITCH 为 True 时使用！
        self.SWITCH = True #False #True   # 定义两种数据爬取方式 True 正向爬取数据，False 则通过字段反推(暂不支持)。

    def start_requests(self):

        item = MGItem()
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
        item["app"] = "咪咕阅读"

        for index, url in enumerate(utils.urls):
            if url == "https://www.migu.cn/read.html":
                # 获取首页top排行榜数据！
                item["type"] = utils.Types[index]
                response = scrapy.Request(url=url, meta=copy.deepcopy({"meta": item}), callback=self.getHtml)
                yield response
            else:
                for page in range(1,201):
                    url = url.format(page=page)
                    item["type"] = utils.Types[index]
                    response = scrapy.Request(url=url, meta=copy.deepcopy({"meta": item}), callback=self.getOtherHtml)
                    yield response

    def getHtml(self, response):

        item = response.meta["meta"]
        hrefs = list(set(response.xpath(r'//*[@id="js_rank_container"]/div/div[1]/ul/*/a/@href').extract()))
        hrefs.extend(list(set(response.xpath(r'//*[@id="js_rank_container"]/div/div[2]/ul/*/a/@href').extract())))
        hrefs.extend(list(set(response.xpath(r'//*[@id="js_rank_container"]/div/div[3]/ul/*/a/@href').extract())))

        for href in hrefs:
            item["uid"] = href.split("/")[-1][:-5]
            response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getDetail)
            yield response

    def getOtherHtml(self, response):

        item = response.meta["meta"]
        hrefs = response.xpath(r'/html/body/div[4]/div[2]/ul/*/a/@href').extract()
        if hrefs == []:
            yield None
        for href in hrefs:
            item["uid"] = href.split("/")[-1][:-5]
            response = scrapy.Request(url=href, meta=copy.deepcopy({"meta": item}), callback=self.getDetail)
            yield response

    def getDetail(self, response):

        item = response.meta["meta"]
        item["name"] = response.xpath(r'string(/html/body/div[4]/div[1]/div[1]/h1)').extract_first().strip()
        item["author"] = response.xpath(r'string(/html/body/div[4]/div[1]/div[1]/div/div[2]/div[1])').extract_first().split("：")[-1].strip()
        item["publish"] = response.xpath(r'string(/html/body/div[4]/div[1]/div[1]/div/div[2]/div[2])').extract_first().split("：")[-1].strip()
        item["classify"] = response.xpath(r'string(/html/body/div[4]/div[1]/div[1]/div/div[2]/div[4])').extract_first().split("：")[-1].strip()
        item["ptime"] = response.xpath(r'string(/html/body/div[4]/div[1]/div[1]/div/div[2]/div[6])').extract_first().split("：")[-1].strip()
        item["label"] = response.xpath(r'string(/html/body/div[4]/div[1]/div[1]/div/div[2]/div[7])').extract_first().split("：")[-1].strip()
        #作者：	夏半秋
        yield item
