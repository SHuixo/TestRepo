# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy

import requests
from LEScrapy.items import LEItem
import logging
import scrapy
import re


class YKSpider(scrapy.Spider):
    name = 'LE'

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.Type = ['电视剧', '电影', '综艺', '动漫']
        self.ListUrls = [
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=2&or=4&stt=1&vt=180001&s=1",
            ##剧集热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=2&or=5&stt=1&vt=180001&s=1",
            ##剧集最新
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=1&or=4&stt=1&vt=180001&s=1",
            ##电影热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=1&or=1&stt=1&vt=180001&s=1",
            ##电影最新
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=11&or=4&stt=1&s=3",
            ##综艺热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=11&or=7&stt=1&s=3",
            ##综艺最新
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=5&or=4&stt=1&s=1",
            ##动漫热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=5&or=5&stt=1&s=1"
            ##动漫最新
        ]
        self.LEUrl = "http://www.le.com/ptv/vplay/{vid}.html"
        self.Maps = {"cg=2&": 0, "cg=1&": 1, "cg=11&": 2, "cg=5&": 3}

    def start_requests(self):

        for reqUrl in self.ListUrls:
            logging.warning("Start reqUrl {url}".format(url=reqUrl))
            lindex = [self.Maps[key] for key in self.Maps if key in reqUrl][0]
            for lpage in range(1, 20):
                logging.warning("start reqUrl page at {page}".format(page=lpage))
                resHtml = requests.get(reqUrl.format(lpage=lpage))
                resHtml.encoding = 'utf-8'
                resHtml = resHtml.text
                resData = re.search(r'"data":{"more":(.*?)}}', resHtml).group(1)
                if resData == "false":
                    break;
                vids = re.findall(r'"vids":"(.*?)",', resHtml)
                for vid in vids:
                    if vid is not None:
                        for vid in vid.split(','):
                            item = LEItem()
                            item["uid"] = vid
                            url = self.LEUrl.format(vid = vid)
                            yield scrapy.Request(url=url, meta={"meta":copy.deepcopy(item)},callback= lambda response, index = lindex: self.parseItemDetails(response, index))
            logging.warning("finish reqUrl all page")
        logging.warning("Finish all reqUrls")

    def parseItemDetails(self, response, index):
        item = response.meta["meta"]
        reshtml = response.text
        errmsg = str(response.xpath('string(/html/body/div[2]/div/div[2]/h2)').extract_first()[:2])
        badmsg = str(re.findall(r'<head><title>(.*?)</title></head>',reshtml))

        if "抱歉" != errmsg and "502 Bad Gateway" not in badmsg and reshtml is not None:
            item["title"] = self.strRegex.sub('',str(re.search(r'pTitle:"(.*?)",',reshtml).group(1)))
            item["pid"] = re.search(r'pid:(.*?),',reshtml).group(1)
            item["hid"] = None
            ##演员
            reGroup = re.search(r'<b>主演：</b><span>(.*?)</span>',reshtml)
            if reGroup is not None:
                item["actor"] = str(re.findall(r'title="(.*?)"', reGroup.group(1)))
            else:
                item["actor"] = None

            reAll = re.findall(r'>(.*?)</a>', re.search(r'<b>类型：</b><span>(.*?)</span>',reshtml))
            if reAll is not None:
                item["category"] = str(reAll.group(1))
            else:
                item["category"] = None
            item["name"] = self.strRegex.sub('',str(re.search(r'title:"(.*?)",',reshtml).group(1)))
            item["type"] = self.Type[index]
            yield item
        else:
            logging.warning("Err No Item at uid {}".format(item["uid"]))
