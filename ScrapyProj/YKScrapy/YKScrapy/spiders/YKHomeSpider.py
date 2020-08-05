# -*- coding: utf-8 -*-
#使用selenium解决动态加载数据抓取
import copy
import csv
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
    name = 'YKHome'

    def __init__(self):
        #chrome浏览器
        self.timeout = 30
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser_options.add_argument('lang=zh_CN.utf-8')
        self.url = "https://www.youku.com"
        self.TvUrl = "https://v.youku.com/v_show/id_{ID}.html"
        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.CatMaps = {"电视剧": 0, "电影": 1, "综艺": 2, "动漫": 3, "少儿":4,"微电影":5,"教育":5}
        self.Funcs = [self.getTVItem,self.parseItem,self.getShowItem,self.getTVItem,self.getTVItem,self.getOtherItem]

    def start_requests(self):
        ## 从HomeUrl爬取入手！！
        yield scrapy.Request(url=self.url,callback=self.getOtherHtml,dont_filter=True)

    def getOtherHtml(self,response):

        resHtml = response.text
        if "404 Not Found" == re.search(r'<title>(.*?)</title>', resHtml).group(1):
            yield None
        elif "亲，访问受限了" == re.search(r'<title>(.*?)</title>', resHtml).group(1):
            print("err，访问受限了,需要人工验证喽！！")
            yield None
        else:
            hrefs = re.findall(r'href="(.*?)"',resHtml,re.S|re.M|re.I)
            hrefs.extend(re.findall(r'videoLink":"(.*?)"',resHtml,re.S|re.M|re.I))
            hrefs.extend(re.findall(r'link":"(.*?)"',resHtml,re.S|re.M|re.I))
            hrefs = list(set(hrefs))
            for href in hrefs:
                if "v.youku.com" in href:
                    print(href)
                    yield scrapy.Request(url="https:"+href,callback=self.getHtml,dont_filter=True)
                else:
                    continue

    def getHtml(self,response):
        print('11')
        resHtml = response.text
        url = response.url
        if "404 Not Found" == re.search(r'<title>(.*?)</title>', resHtml).group(1):
            yield None
        else:
            cNgroup = re.search(r"catName: '(.*?)',",resHtml)
            if cNgroup is not None:
                catName = cNgroup.group(1).strip()
            else:
                catName = '其他'
            index = [self.CatMaps[key] for key in self.CatMaps if key in catName]
            if index != []:
                index = index[0]
                tFlag = response.xpath('string(//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div/a)').extract_first()
                if tFlag == "TA的视频":
                    response = scrapy.Request(url=url,callback=self.getOtherItem,dont_filter=True)
                    yield response
                else:
                    yield scrapy.Request(url=url,callback=self.Funcs[index],dont_filter=True)
            else:
                response = scrapy.Request(url=url,callback=self.parseItem,dont_filter=True)
                yield response

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
                for lpage in range(1, 4):
                    action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt/a[{lpage}]/span'.format(lpage=lpage))
                    ActionChains(self.browser).move_to_element(action).click(action).perform()
                    time.sleep(1)
                    res_field = self.browser.page_source
                    if res_field:
                        field_sel = etree.HTML(res_field)
                        if index == 0:
                            refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href'))
                        if index == 4:
                            refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/*/a/@href'))
                action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt/a[4]/span')
                ActionChains(self.browser).move_to_element(action).click(action).perform()
                res_field = self.browser.page_source
                field_sel = etree.HTML(res_field)
                lpart = field_sel.xpath('string(//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dd)')
                lparts = lpart.split('-')
                res_pages = len(lparts)
                if len(lparts[-1])>3:
                    res_pages = res_pages + 1
                for rpage in range(1, res_pages):
                    action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dd/a[{rpage}]'.format(rpage=rpage))
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
                    if index == 0:
                        refList.extend(resEtree.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href'))
                    if index == 4:
                        refList.extend(resEtree.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/*/a/@href'))
                elif res_pages > 1:
                    for page in range(1, res_pages):
                        action = self.browser.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/dt/a[{page}]/span'.format(page=page))
                        ActionChains(self.browser).move_to_element(action).click(action).perform()
                        time.sleep(1)
                        res_field = self.browser.page_source
                        if res_field:
                            field_sel = etree.HTML(res_field)
                            if index == 0:
                                refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/a/@href'))
                            if index == 4:
                                refList.extend(field_sel.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/*/a/@href'))
        self.browser.close()
        if refList != []:
            for refUrl in refList:
                response = scrapy.Request(url=refUrl,callback=self.parseItem)
                yield response
        logging.warning("完成执行 getTVItem -> {}".format(self.TvUrl.format(ID=id)))

    def getOtherItem(self,response):
        hrefs = response.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/*/a/@href').extract()
        for href in hrefs:
            yield scrapy.Request(url=href,callback=self.parseItem,dont_filter=True)

    def getShowItem(self,response):
        refList = response.xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/*/a/@href').extract()
        logging.warning("开始执行 getShowItem -> {}".format(refList))
        for refUrl in refList:
            response = scrapy.Request(url=refUrl,callback=self.parseItem)
            yield response
        logging.warning("开始执行 getShowItem -> {}".format(self.TvUrl.format(ID=id)))

    def parseItem(self, response):
        resHtml = response.text
        if "404 Not Found" == re.search(r'<title>(.*?)</title>', resHtml).group(1):
            yield None
        else:
            item = YKItem()
            if self.SWITCH:
                item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="module_basic_dayu_sub"]/div/div[1]/a[1])').extract_first())
                item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div)').extract_first())
                if '内容简介' in item["category"]:
                    item["category"] = item["category"].split('内容简介')[1]
            else:
                item["title"] = None
                item["category"] = None

            item["name"] = self.strRegex.sub('',response.xpath('string(//*[@id="left-title-content-wrap"])').extract_first())
            item["uid"] = re.search(r"videoId: '(.*?)',",resHtml).group(1).strip()
            item["pid"] = re.search(r"showid: '(.*?)',",resHtml).group(1).strip()
            item["hid"] = re.search(r"videoId2: '(.*?)',",resHtml).group(1).strip()
            item["type"] = re.search(r"catName: '(.*?)',",resHtml).group(1).strip()
            item["actor"] = None
            item["app"] = "YOUKU"
            yield item
