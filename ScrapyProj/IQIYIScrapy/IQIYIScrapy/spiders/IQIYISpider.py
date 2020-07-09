# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy
import requests
import logging
import scrapy
import re
from IQIYIScrapy.items import IQIYItem


class LESpider(scrapy.Spider):
    name = 'IQIYI'

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.Type = ['电视剧', '电影', '综艺', '动漫']
        self.ListUrls = [
            "https://list.iqiyi.com/www/2/-------------24-{lPage}-1-iqiyi--.html", ##电视剧综合排序
            "https://list.iqiyi.com/www/2/-------------11-{lPage}-1-iqiyi--.html", ##电视剧热播榜
            "https://list.iqiyi.com/www/2/-------------4-{lPage}-1-iqiyi--.html",  ##电视剧新上线
            "https://list.iqiyi.com/www/1/-------------24-{lPage}-1-iqiyi--.html", ##电影综合排序
            "https://list.iqiyi.com/www/1/-------------11-{lPage}-1-iqiyi--.html", ##电影热播榜
            "https://list.iqiyi.com/www/1/-------------8-{lPage}-1-iqiyi--.html",  ##电影好评榜
            "https://list.iqiyi.com/www/1/-------------4-{lPage}-1-iqiyi--.html",  ##电影新上线
            "https://list.iqiyi.com/www/6/-------------24-{lPage}-1-iqiyi--.html", ##综艺综合排序
            "https://list.iqiyi.com/www/6/-------------11-{lPage}-1-iqiyi--.html", ##综艺热播榜
            "https://list.iqiyi.com/www/6/-------------4-{lPage}-1-iqiyi--.html",  ##综艺新上线
            "https://list.iqiyi.com/www/4/-------------24-{lPage}-1-iqiyi--.html",  ##动漫综合排序
            "https://list.iqiyi.com/www/4/-------------11-{lPage}-1-iqiyi--.html", ##动漫热播榜
            "https://list.iqiyi.com/www/4/-------------4-{lPage}-1-iqiyi--.html"   ##动漫新上线
        ]
        self.Maps = {"/2/": 0, "/1/": 1, "/6/": 2, "/4/": 3}
        self.Func = [self.ParseTvPage, self.ParseMoviePage, self.ParseShowPage, self.ParseAnimalPage]

    def start_requests(self):

        for reqUrl in self.ListUrls:
            logging.warning("Start reqUrl {url}".format(url=reqUrl))
            lindex = [self.Maps[key] for key in self.Maps if key in reqUrl][0]
            for lpage in range(1, 20):
                logging.warning("start reqUrl page at {page}".format(page=lpage))
                yield scrapy.Request(url=reqUrl.format(lPage=lpage), meta={"index":copy.deepcopy(lindex)},callback= self.getHtml)
            logging.warning("finish reqUrl all page")
        logging.warning("Finish all reqUrls")

    def getHtml(self,response):

        lindex = response.meta["index"]
        playUrls = re.findall(r'playUrl":"(.*?)",', response.text)
        for playurl in playUrls:
            yield scrapy.Request(url=playurl,callback= self.Func[lindex])
    #待完善
    def ParseTvPage(self, response):

        errmsg = re.findall(r'<title>(.*?)</title>',response.text)[0][:3]
        if '404' == errmsg:
            yield


    def parseItem(self, response, index):
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
                item["actor"] = self.strRegex.sub('',str(re.findall(r'title="(.*?)"', reGroup.group(1))))
            else:
                item["actor"] = None

            reAll = re.findall(r'>(.*?)</a>', re.search(r'<b>类型：</b><span>(.*?)</span>',reshtml))
            if reAll is not None:
                item["category"] = self.strRegex.sub('',str(reAll.group(1)).replace(",","；").replace("|","；"))
            else:
                item["category"] = None
            item["name"] = self.strRegex.sub('',str(re.search(r'title:"(.*?)",',reshtml).group(1)))
            item["type"] = self.Type[index]
            item["app"] = "LE"
            yield item
        else:
            logging.warning("Err No Item at uid {}".format(item["uid"]))
