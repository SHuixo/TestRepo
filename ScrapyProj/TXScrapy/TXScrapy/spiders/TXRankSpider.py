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
    name = 'TXRank'
    url = ["https://v.qq.com"]

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.url = "https://v.qq.com"
        self.Maps = {"tv": 0, "movie": 1, "variety": 2, "cartoon": 0}
        self.TypeMaps = {"电视剧":0, "电影":1, "综艺":2, "动漫":0,"少儿":0,"纪录片":3}
        self.Funcs = [self.getTvItem,self.getMovieItem,self.getVarietyItem,self.getVlogItem]

    def start_requests(self):

        response = scrapy.Request(url=self.url,callback=self.getHtml)
        yield response

    def getHtml(self, response):
        resHtml = response.text
        if len(resHtml) > 10:
            hrefs = re.findall(r'href="(.*?)"', resHtml, re.M|re.I|re.S)
            hrefs = list(set(hrefs))
            print(hrefs)
            for href in hrefs:
                if 'https://v.qq.com/x' in href:
                    response = scrapy.Request(url=href,callback=self.getOtherItem)
                    yield response
                else:
                    continue

    def getOtherItem(self,response):

        url = response.url
        ttype = re.search(r'type_name":(.*?),',response.text).group(1).replace('"','')
        lindex = [self.TypeMaps[key] for key in self.TypeMaps if key in ttype]
        if lindex != []:
            index = lindex[0]
            response = scrapy.Request(url=url,callback=self.Funcs[index],dont_filter=True)
            yield response
        elif lindex == []:
            item = TXItem()
            item["pid"] = None
            item["hid"] = None
            item["actor"] = None
            item["title"] = None
            item["category"] = None
            hrefs = response.xpath(r'/html/body/div[1]/div[3]/div[2]/div[2]/div/div/div[1]/div/div[1]/ul/*/a/@href').extract()
            titles = response.xpath(r'/html/body/div[1]/div[3]/div[2]/div[2]/div/div/div[1]/div/div[1]/ul/*/a/@title').extract()
            for ltag, title in enumerate(titles):
                item["uid"] = re.search(r'page/(.*?).html',hrefs[ltag]).group(1).strip()
                item["name"] = title
                item["type"] = re.search(r'type_name":(.*?),',response.text).group(1).replace('"','')
                item["app"] = "TENCENT"
                yield item

    def getTvItem(self, response):
        href = response.url
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first())
            item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[4])').extract_first())
            item["actor"] = None
            if '/page' in href:
                rhtml = re.search(r'page/(.*?).html',href).group(1).strip()
            elif '/cover' in href:
                rhtml = re.search(r'cover/(.*?).html',href).group(1).strip()
            if len(rhtml.split("/")) == 1:
                item["pid"] =rhtml
            elif len(rhtml.split("/")) == 2:
                item["pid"] =rhtml.split("/")[0]
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
        href = response.url
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            vids = []
            if '/cover/' in href:
                item["title"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first())
                item["category"] = self.strRegex.sub('',response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[3])').extract_first())
                item["actor"] = None
                rhtml = re.search(r'cover/(.*?).html',href).group(1).strip()
                if len(rhtml.split("/")) == 1:
                    item["pid"] =rhtml
                elif len(rhtml.split("/")) == 2:
                    item["pid"] =rhtml.split("/")[0]
            elif '/page/' in href:
                rhtml = re.search(r'page/(.*?).html',href).group(1).strip()
                if len(rhtml.split("/")) == 1:
                    vids.append(rhtml)
                item["title"] = None
                item["category"] = None
                item["actor"] = None
                item["pid"] = None
            item["hid"] = None
            ## 获得每一集的ID
            vidGroup = re.search(r'{"vid":\[(.*?)\],',reshtml)
            if vidGroup is not None:
                vids.extend(vidGroup.group(1).replace('"','').split(','))
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
