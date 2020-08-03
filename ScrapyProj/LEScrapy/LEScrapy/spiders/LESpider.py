# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy
import csv

import requests
from LEScrapy.items import LEItem
import logging
import scrapy
import re


class LESpider(scrapy.Spider):
    name = 'LE'

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.Type = ['电视剧', '电影', '综艺', '动漫']
        self.ListUrls = [
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=2&or=4&stt=1&vt=180001&s=1", ##剧集热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=2&or=5&stt=1&vt=180001&s=1", ##剧集最新
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=1&or=4&stt=1&vt=180001&s=1", ##电影热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=1&or=1&stt=1&vt=180001&s=1", ##电影最新
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=11&or=4&stt=1&s=3",          ##综艺热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=11&or=7&stt=1&s=3",          ##综艺最新
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=5&or=4&stt=1&s=1",           ##动漫热播
            "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={lpage}&ph=420001&dt=1&cg=5&or=5&stt=1&s=1"            ##动漫最新
        ]
        self.LEUrl = "http://www.le.com/ptv/vplay/{vid}.html"
        self.Maps = {"cg=2&": 0, "cg=1&": 1, "cg=11&": 2, "cg=5&": 3}
        self.TypeMaps = {"1":"电影","2":"电视剧","3":"娱乐","5":"动漫","9":"音乐","11":"综艺","16":"纪录片","34":"亲子",
                         "20":"风尚","22":"财经","14":"汽车","23":"旅游","30":"热点","1035":"全景","1009":"资讯","1021":"教育"}
        self.SWITCH = False #True #False   #用于从网站获取内容( True )和从本地文件( False )获取内容的切换。
        self.File = r"./checkLE.txt"

    def start_requests(self):
        if self.SWITCH:
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
                    for lvid in vids:
                        if lvid is not None:
                            for vid in lvid.split(','):
                                item = LEItem()
                                item["uid"] = vid
                                url = self.LEUrl.format(vid = vid)
                                yield scrapy.Request(url=url, meta={"meta":copy.deepcopy(item)},callback= self.parseItemDetails)
                logging.warning("finish reqUrl all page")
            logging.warning("Finish all reqUrls")
        else:
            #从本地文件读取入手！！
            with open(self.File, 'r', encoding='UTF-8') as csvfile:
                lines = csv.reader(csvfile)
                for line in lines:
                    item = LEItem()
                    item["uid"] = line[0]
                    ## 判断读取的为纯数字，否则pass
                    if str(line[0]).isdigit():
                        logging.warning("Start spider 读取到 line= {}".format(line[0]))
                        url = self.LEUrl.format(vid=line[0])
                        yield scrapy.Request(url=url, meta={"meta": copy.deepcopy(item)}, callback=self.parseItemDetails, dont_filter=True)
                    else:
                        continue
                logging.warning("读取完毕！！")

    def parseItemDetails(self, response):
        item = response.meta["meta"]
        reshtml = response.text

        errmsg = str(response.xpath('string(/html/body/div[2]/div/div[2]/h2)').extract_first()[:2])
        badmsg = str(re.findall(r'<head><title>(.*?)</title></head>',reshtml))

        if "抱歉" != errmsg and "502 Bad Gateway" not in badmsg and reshtml is not None:
            item["title"] = self.strRegex.sub('',str(re.search(r'pTitle:"(.*?)",',reshtml).group(1)))
            item["pid"] = re.search(r'pid:(.*?),',reshtml).group(1).strip()
            item["hid"] = None
            reGroup = re.search(r'<!--主演-->(.*?)<!--简介',str(reshtml))
            reAll = re.search(r'<!--类型-->(.*?)<!--主演-->',str(reshtml))
            if reGroup is not None:
                item["actor"] = self.strRegex.sub('',str(re.findall(r'title="(.*?)"', str(reGroup.group(1)))))
                item["category"] = self.strRegex.sub('',str(re.findall(r'title="(.*?)"', str(reAll.group(1)))))
            else:
                item["actor"] = None
                item["category"] = None
            item["name"] = self.strRegex.sub('',str(re.search(r'title:"(.*?)",',reshtml).group(1)))
            try:
                item["type"] = self.TypeMaps[str(re.search(r'cid:(.*?),',reshtml).group(1)).strip()]  ##频道id
            except KeyError:
                item["type"] = "其他"
            item["app"] = "LE"
            yield item
        else:
            logging.warning("Err No Item at uid {}".format(item["uid"]))
