# -*- coding: utf-8 -*-
#使用selenium解决动态加载数据抓取
import copy
import time
from YKScrapy.items import YKItem
import scrapy
import re
from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from YKScrapy.spiders import utils
import logging

class YKSpider(scrapy.Spider):
    name = 'YK'

    def __init__(self):
        #chrome浏览器
        self.timeout = 30
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser_options.add_argument('lang=zh_CN.utf-8')

        self.TvUrl = "https://v.youku.com/v_show/id_{ID}.html"
        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.Type = ['电视剧', '电影', '综艺', '动漫']
        self.Maps = {"c=97": 0, "c=96": 1, "c=85": 2, "c=100": 3}
        self.Funcs = [self.getTVItem,self.parseItem,self.getShowItem,self.getTVItem]

    def start_requests(self):
        for reqUrl in utils.YK_Urls:
            logging.warning("开始执行 reqUrl -> {}".format(reqUrl))
            for area in utils.YK_Areas:
                logging.warning("开始执行 reqUrl area -> {}".format(area))
                for lpage in range(1,17):
                    logging.warning("开始执行 reqUrl area lpage -> {}".format(lpage))
                    yield scrapy.Request(url=reqUrl.format(area=area,lpage=lpage),meta=copy.deepcopy({"url":reqUrl}),callback=self.getHtml)
                logging.warning("完成执行 reqUrl area lpage !!")
            logging.warning("完成执行 reqUrl area !!")
        logging.warning("完成执行 reqUrl!!")

    def getHtml(self,response):
        refUrl = response.meta["url"]
        resHtml = response.text

        resData = re.search(r'data":(.*?),"code"',resHtml).group(1)
        if resData == "[]":
            yield
        videoIDs = re.findall(r'videoId":"(.*?)",',resData)
        for videoID in videoIDs:
            index = [self.Maps[key] for key in self.Maps if key in refUrl][0]
            yield scrapy.Request(url=self.TvUrl.format(ID=videoID),meta=copy.deepcopy({"index":index,"id":videoID}),callback=self.Funcs[index])

    def getTVItem(self, response):
        index = response.meta["index"]
        id = response.meta["id"]
        self.browser = webdriver.Chrome(chrome_options=self.browser_options)
        logging.warning("开始执行 getTVItem -> {}".format(self.TvUrl.format(ID=id)))
        self.browser.get(self.TvUrl.format(ID=id))
        resHtml = self.browser.page_source
        refList = []
        resEtree = etree.HTML(resHtml)
        errmsg = str(resEtree.xpath('string(//*[@id="root"]/div/div/div[2])'))
        if "错误码：" != errmsg:
            #获取该优酷影视是否有多个分集模块
            lpart = resEtree.xpath('string(//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt)')
            if lpart[-4:] == "更多视频":
                for page in range(1, 4):
                    action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt/a[{page}]/span'.format(page=page))
                    ActionChains(self.browser).move_to_element(action).click(action).perform()
                    time.sleep(1)
                    res_field = self.browser.page_source
                    if res_field:
                        field_sel = etree.HTML(res_field)
                        refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href'))

                action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt/a[4]/span')
                ActionChains(self.browser).move_to_element(action).click(action).perform()
                res_field = self.browser.page_source
                field_sel = etree.HTML(res_field)
                lpart = field_sel.xpath('string(//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dd)')
                lparts = lpart.split('-')
                res_pages = len(lparts)
                if len(lparts[-1])>3:
                    res_pages = res_pages + 1
                for page in range(1, res_pages):
                    action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dd/a[{page}]'.format(page=page))
                    ActionChains(self.browser).move_to_element(action).click(action).perform()
                    time.sleep(1)
                    res_field = self.browser.page_source
                    if res_field:
                        field_sel = etree.HTML(res_field)
                        refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href'))
            else:
                lparts = lpart.split('-')
                res_pages = len(lparts)
                if len(lparts[-1])>3:
                    res_pages = res_pages + 1
                if res_pages == 1:
                    refList = resEtree.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href')
                elif res_pages > 1:
                    for page in range(1, res_pages):
                        action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt/a[{page}]/span'.format(page=page))
                        ActionChains(self.browser).move_to_element(action).click(action).perform()
                        time.sleep(1)
                        res_field = self.browser.page_source
                        if res_field:
                            field_sel = etree.HTML(res_field)
                            refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href'))
        self.browser.close()
        if refList != []:
            for refUrl in refList:
                response = scrapy.Request(url=refUrl,meta=copy.deepcopy({"index":index}),callback=self.parseItem)
                yield response
        logging.warning("完成执行 getTVItem -> {}".format(self.TvUrl.format(ID=id)))

    def getMovieItem(self, response):
        return None

    def getShowItem(self,response):
        index = response.meta["index"]
        refList = response.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/*/a/@href').extract()
        logging.warning("开始执行 getShowItem -> {}".format(refList))
        for refUrl in refList:
            response = scrapy.Request(url=refUrl,meta=copy.deepcopy({"index":index}),callback=self.parseItem)
            yield response
        logging.warning("开始执行 getShowItem -> {}".format(self.TvUrl.format(ID=id)))

    def parseItem(self, response):
        index = response.meta["index"]
        resHtml = response.text
        item = YKItem()

        item["title"] = response.xpath('string(//*[@id="module_basic_dayu_sub"]/div/div[1]/a[1])').extract_first()
        item["category"] = response.xpath('string(//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div)').extract_first()
        if '内容简介' in item["category"]:
            item["category"] = item["category"].split('内容简介')[1]

        item["name"] = self.strRegex.sub('',response.xpath('string(//*[@id="left-title-content-wrap"])').extract_first())
        item["uid"] = re.search(r"videoId: '(.*?)',",resHtml).group(1)
        item["pid"] = re.search(r"showid: '(.*?)',",resHtml).group(1)
        item["hid"] = re.search(r"videoId2: '(.*?)',",resHtml).group(1)
        item["type"] = self.Type[index]
        item["actor"] = None
        item["app"] = "YOUKU"
        yield item
