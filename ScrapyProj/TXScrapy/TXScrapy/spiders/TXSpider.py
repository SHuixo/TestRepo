# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy
import csv
import logging
import scrapy
import re

from TXScrapy.items import TXItem
from TXScrapy.spiders import utils


class TXSpider(scrapy.Spider):
    name = 'TX'

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')

        self.Areas = [utils.TX_TVAreas, utils.TX_MovieAreas, utils.TX_VarietyAreas, utils.TX_CartoonAreas,utils.TX_ChildAreas]
        self.Maps = {"tv": 0, "movie": 1, "variety": 2, "cartoon": 0, "child":0}
        self.TypeMaps = {"电视剧":0, "电影":1, "综艺":2, "动漫":0,"少儿":0,"纪录片":3}
        self.Funcs = [self.getTvItem,self.getMovieItem,self.getVarietyItem,self.getVlogItem]
        self.SWITCH = False   #用于从网站获取内容(True)和从本地文件(False)获取内容的切换。
        self.TxUrl = "https://v.qq.com/x/cover/{ID}.html"
        self.File = r"./checkTX.txt"

    def start_requests(self):
        if self.SWITCH:
            for reqUrl in utils.TX_Urls:
                logging.warning("start requrl {}".format(reqUrl))
                index = [self.Maps[key] for key in self.Maps if key in reqUrl][0]
                Area = self.Areas[index]
                for iarea in Area:
                    logging.warning("start requrl  iarea{}".format(iarea))
                    for lpage in range(1,50):
                        logging.warning("start requrl  iarea lpage{}".format(lpage))
                        response = scrapy.Request(url=reqUrl.format(iarea=iarea,ofset=lpage*30),meta=copy.deepcopy({"index":index}),callback=self.getHtml)
                        yield response
                    logging.warning("finish reqUrl all page")
                logging.warning("finish reqUrl all area")
            logging.warning("Finish all reqUrls")
        else:
            #从本地文件读取入手！！
            with open(self.File) as csvfile:
                lines = csv.reader(csvfile)
                for line in lines:
                    logging.warning("Start spider 读取到 line= {}".format(line[0]))
                    yield scrapy.Request(url=self.TxUrl.format(ID=line[0]),meta=copy.deepcopy({"ID":line[0]}),callback=self.getOtherItem,dont_filter=True)
                logging.warning("读取完毕！！")

    def getOtherItem(self,response):
        ID = response.meta["ID"]
        type = re.search(r'type_name":"(.*?)"',response.text).group(1)
        index = [self.TypeMaps[key] for key in self.TypeMaps if key in type][0]
        response = scrapy.Request(url=self.TxUrl.format(ID=ID),meta=copy.deepcopy({"href":self.TxUrl.format(ID=ID)}),callback=self.Funcs[index],dont_filter=True)
        yield response

    def getHtml(self, response):
        index = response.meta["index"]
        resHtml = response.text
        if len(resHtml) > 10:
            hrefs = response.xpath('/html/body/*/a/@href').extract()
            hrefs.extend(response.xpath('/html/body/div/div/div[2]/*/a/@href').extract())
            hrefs = list(set(hrefs))
            for href in hrefs:
                response = scrapy.Request(url=href,meta=copy.deepcopy({"href": href}),callback=self.Funcs[index])
                yield response

    def getTvItem(self, response):
        href = response.meta["href"]
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first())
            item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[4])').extract_first())
            item["actor"] = None
            item["pid"] = re.search(r'cover/(.*?).html',href)
            item["hid"] = None
            ## 获得每一集的ID
            vidGroup = re.search(r'{"vid":\[(.*?)\],',reshtml)
            if vidGroup is not None:
                vids = vidGroup.group(1)
                if len(vids) > 2:
                    vids = vids.replace('"','').split(',')
                    for vid in vids:
                        item["uid"] = vid
                        reqUrl = href[:-5]+'/'+vid+'.html'
                        response = scrapy.Request(url=reqUrl,meta=copy.deepcopy({"meta":item}),callback=self.getItem)
                        yield response
                else:
                    logging.warning("Err no vids at href {}".format(href))
            else:
                logging.warning("Err no vidGroup at href {}".format(href))
        else:
            logging.warning("Err No reshtml at href {}".format(href))

    def getMovieItem(self,response):
        href = response.meta["href"]
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first())
            item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[3])').extract_first())
            item["actor"] = None
            item["pid"] = re.search(r'cover/(.*?).html',href).group(1).strip()
            item["hid"] = None
            ## 获得每一集的ID
            vidGroup = re.search(r'{"vid":\[(.*?)\],',reshtml)
            if vidGroup is not None:
                vids = vidGroup.group(1).replace('"','').split(',')
                for vid in vids:
                    item["uid"] = vid
                    reqUrl = href[:-5]+'/'+vid+'.html'
                    response = scrapy.Request(url=reqUrl,meta=copy.deepcopy({"meta":item}),callback=self.getItem)
                    yield response
            else:
                logging.warning("Err no vidGroup at href {}".format(href))
        else:
            logging.warning("Err No reshtml at href {}".format(href))

    def getVarietyItem(self,response):
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first())
            item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div[2]/div[2]/div[1]/div[2]/div/div[3])').extract_first())
            item["actor"] = None
            item["pid"] = None
            item["hid"] = None
            hrefs = response.xpath('//*[@id="video_scroll_wrap"]/div[5]/div/ul/*/a[1]/@href').extract()
            for href in hrefs:
                if href is not None:
                    item["uid"] = href[:-5].split('/')[-1]
                    reqUrl = "https://v.qq.com" + href
                    response = scrapy.Request(url=reqUrl,meta=copy.deepcopy({"meta":item}),callback=self.getItem)
                    yield response
                else:
                    logging.warning("Err href is None")
        else:
            logging.warning("Err No reshtml at getVarietyItem")

    def getVlogItem(self,response):
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div/h2/a)').extract_first())
            item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[4])').extract_first())
            item["actor"] = None
            item["hid"] = None
            hrefs = response.xpath('//*[@id="video_scroll_wrap"]/div[4]/div/div/ul/*/a[1]/@href').extract()
            for href in hrefs:
                if href is not None:
                    lhref = href[:-5].split('/')
                    item["uid"] = lhref[-1]
                    item["pid"] = lhref[-2]
                    reqUrl = "https://v.qq.com" + href
                    response = scrapy.Request(url=reqUrl,meta=copy.deepcopy({"meta":item}),callback=self.getItem)
                    yield response
                else:
                    logging.warning("Err href is None")
        else:
            logging.warning("Err No reshtml at getVlogItem")

    def getItem(self,response):
        item = response.meta["meta"]
        item["type"] = re.search(r'type_name":"(.*?)"',response.text).group(1)
        if item["type"] == "综艺":
            name = response.xpath('string(//*[@id="container_player"]/div[2]/div[2]/div[1]/div[1]/h1)').extract_first()
        else:
            name = response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[1]/h1)').extract_first()
        ##预防包含非正常符号，导致出错
        item["name"] = self.strRegex.sub('',name)
        item["app"] = "TENCENT"
        yield item
