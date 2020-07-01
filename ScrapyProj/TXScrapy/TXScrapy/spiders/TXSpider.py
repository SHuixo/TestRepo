# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy
from TXScrapy.items import TXItem
import logging
import scrapy
import re

from TXScrapy.TXScrapy.spiders import utils


class TXSpider(scrapy.Spider):
    name = 'TX'

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.Type = ['电视剧', '电影', '综艺', '动漫']
        self.Areas = [utils.TX_TVAreas, utils.TX_MovieAreas, utils.TX_VarietyAreas, utils.TX_CartoonAreas]
        self.Maps = {"tv": 0, "movie": 1, "variety": 2, "cartoon": 3}
        self.Funcs = [self.getTvItem,self.getMovieItem,self.getVarietyItem,self.getTvItem]

    def start_requests(self):
        for reqUrl in utils.TX_Urls:
            index = [self.Maps[key] for key in self.Maps if key in reqUrl][0]
            Area = self.Areas[index]
            for iarea in Area:
                for lpage in range(1,50):
                    response = scrapy.Request(url=reqUrl.format(iarea=iarea,ofset=lpage*30),meta=copy.deepcopy({"index":index}),callback=self.getHtml)
                    yield response
                logging.warning("finish reqUrl all page")
            logging.warning("finish reqUrl all area")
        logging.warning("Finish all reqUrls")

    def getHtml(self, response):
        index = response.meta["index"]
        resHtml = response.text
        if len(resHtml) > 10:
            hrefs = response.xpath('/html/body/*/a/@href').extract()
            hrefs.extend(response.xpath('/html/body/div/div/div[2]/*/a/@href').extract())
            hrefs = list(set(hrefs))
            for href in hrefs:
                response = scrapy.Request(url=href,meta=copy.deepcopy({"index": index,"href": href}),callback=self.Funcs[index])
                yield response

    def getTvItem(self, response):
        index = response.meta["index"]
        href = response.meta["href"]
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = str(response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first()).strip()
            item["category"] = str(response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[4])').extract_first()).replace('\n','').replace(' ','').strip()
            item["actor"] = None
            item["pid"] = None
            item["hid"] = None
            ## 获得每一集的ID
            vidGroup = re.search(r'{"vid":\[(.*?)\],',reshtml)
            if vidGroup is not None:
                vids = vidGroup.group(1)
                if len(vids) > 2:
                    vids = vids.replace('"','').split(',')
                    for vid in vids:
                        reqUrl = href[:-5]+'/'+vid+'.html'
                        response2 = scrapy.Request(url=reqUrl)
                        name = str(response2.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[1]/h1)').extract_first()).strip()
                        ##预防包含非正常符号，导致出错
                        item["name"] = self.strRegex.sub('',name)
                        item["type"] = self.Type[index]
                        yield item
                else:
                    logging.warning("Err no vids at href {}".format(href))
            else:
                logging.warning("Err no vidGroup at href {}".format(href))
        else:
            logging.warning("Err No reshtml at href {}".format(href))

    def getMovieItem(self,response):
        index = response.meta["index"]
        href = response.meta["href"]
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = str(response.xpath('string(//*[@id="container_player"]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first()).strip()
            item["category"] = str(response.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[2]/div/div[3])').extract_first()).replace('\n','').replace(' ','').strip()
            item["actor"] = None
            item["pid"] = None
            item["hid"] = None
            ## 获得每一集的ID
            vidGroup = re.search(r'{"vid":\[(.*?)\],',reshtml)
            if vidGroup is not None:
                vids = vidGroup.group(1).replace('"','').split(',')
                for vid in vids:
                    reqUrl = href[:-5]+'/'+vid+'.html'
                    response2 = scrapy.Request(url=reqUrl)
                    name = str(response2.xpath('string(//*[@id="container_player"]/div/div[2]/div[1]/div[1]/h1)').extract_first()).strip()
                    ##预防包含非正常符号，导致出错
                    item["name"] = self.strRegex.sub('',name)
                    item["type"] = self.Type[index]
                    yield item
            else:
                logging.warning("Err no vidGroup at href {}".format(href))
        else:
            logging.warning("Err No reshtml at href {}".format(href))

    def getVarietyItem(self,response):
        index = response.meta["index"]
        reshtml = response.text
        if reshtml is not None:
            item = TXItem()
            item["title"] = str(response.xpath('string(//*[@id="container_player"]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h2/a)').extract_first()).strip()
            item["category"] = str(response.xpath('string(//*[@id="container_player"]/div[2]/div[2]/div[1]/div[2]/div/div[3])').extract_first()).replace('\n','').replace(' ','').strip()
            item["actor"] = None
            item["pid"] = None
            item["hid"] = None
            hrefs = response.xpath('//*[@id="video_scroll_wrap"]/div[5]/div/ul/*/a[1]/@href').extract()
            for href in hrefs:
                if href is not None:
                    vidGroup = re.search(r'/(.*?).html',href)
                    if vidGroup is not None:
                        item["uid"] = vidGroup.group(1).split('/')[-1]
                        reqUrl = "https://v.qq.com" + href
                        response2 = scrapy.Request(url=reqUrl)
                        name = str(response2.xpath('string(//*[@id="container_player"]/div[2]/div[2]/div[1]/div[1]/h1)').extract_first()).strip()
                        ##预防包含非正常符号，导致出错
                        item["name"] = self.strRegex.sub('',name)
                        item["type"] = self.Type[index]
                        yield item
                    else:
                        logging.warning("Err no vidGroup at href {}".format(href))
                else:
                    logging.warning("Err href is None")
        else:
            logging.warning("Err No reshtml at getVarietyItem")
