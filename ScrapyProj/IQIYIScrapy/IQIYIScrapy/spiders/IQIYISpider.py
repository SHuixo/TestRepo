# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy
import random

import requests
import logging
import scrapy
import re
from IQIYIScrapy.items import IQIYItem

from IQIYIScrapy.spiders import utils


class LESpider(scrapy.Spider):
    name = 'IQIYI'

    def __init__(self):

        self.strRegex = re.compile('[^\w\u4e00-\u9fff]')
        self.Type = ['电视剧', '电影', '综艺', '动漫',"纪录片"]
        self.Areas = [utils.TVAreas,utils.MovieAreas,utils.ShowAreas,utils.AnimalAreas,utils.VlogAreas]
        self.Maps = {"channel_id=2": 0, "channel_id=1": 1, "channel_id=6": 2, "channel_id=4": 3, "channel_id=3":4}
        self.Func = [self.ParseTvPage, self.ParseMoviePage, self.ParseShowPage, self.ParseAnimalPage]

    def start_requests(self):

        for reqUrl in utils.IQIYIUrls:
            logging.warning("Start reqUrl {url}".format(url=reqUrl))
            for mode in utils.IQIYIModes:
                logging.warning("Start reqUrl ：{url} | mode： {mode}".format(url=reqUrl,mode=mode))
                lindex = [self.Maps[key] for key in self.Maps if key in reqUrl][0]
                for iarea in self.Areas[lindex]:
                    logging.warning("Start reqUrl :{url}| mode：{mode} | iarea : {iarea}".format(url=reqUrl,mode=mode,iarea=iarea))
                    for lpage in range(1, 20):
                        logging.warning("Start reqUrl :{url}| mode：{mode} | iarea : {iarea} | page : {page}".format(url=reqUrl,mode=mode,iarea=iarea,page=lpage))
                        yield scrapy.Request(url=reqUrl.format(lPage=lpage), meta=copy.deepcopy({"index":lindex}),callback= self.getHtml)
                    logging.warning("finish all page")
                logging.warning("finish all area")
            logging.warning("finish all mode")
        logging.warning("Finish all reqUrl")

    def getHtml(self,response):

        reshtml = response.text
        if re.findall(r'"list":(.*?),', reshtml) == []:
            yield None
        else:
            lindex = response.meta["index"]
            playUrls = re.findall(r'playUrl":"(.*?)",', reshtml)
            albumIds = re.findall(r'"albumId":(.*?),', reshtml)
            titles = re.findall(r'"title":"(.*?)",', reshtml)
            categories = re.findall(r'"categories":(.*?),', reshtml)
            actors = re.findall(r'"people":{(.*?)}', reshtml)
            for tag, playurl in enumerate(playUrls):
                item = IQIYItem()
                item["pid"] = albumIds[tag]
                item["title"] = titles[tag]
                item["category"] = categories[tag]
                item["actor"] = re.findall(r'"name":"(.*?)"}',str(actors[tag]))
                yield scrapy.Request(url=playurl,meta=copy.deepcopy({"item":item,"index":lindex}),callback= self.Func[lindex])


    def ParseTvPage(self, response):

        item = response.meta["item"]
        lindex = response.meta["index"]
        ##获取该电视剧所有集数的属性信息
        PageUrl="https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={aid}&page={page}&size=30"
        reshtml = requests.get(PageUrl.format(aid=item["pid"],page="1"), headers=random.choice(utils.USER_AGENTS)).text
        tvIds = re.findall(r'tvId":(.*?),',reshtml)
        hids = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',reshtml)))
        names = re.findall(r'shortTitle":"(.*?)",',reshtml)
        pages = (int)(re.findall(r'page":(.*?),',reshtml)[0])
        if pages > 1:
            for page in range(2,pages+1):
                reshtml = requests.get(PageUrl.format(aid=item["pid"], page=page), headers=self.headers).text
                tvIds.extend(re.findall(r'tvId":(.*?),',reshtml))
                hids.extend(re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',reshtml))))
                names.extend(re.findall(r'shortTitle":"(.*?)",',reshtml))

        for tvTag, tvid in enumerate(tvIds):
            item["uid"] = tvid
            item["hid"] = hids[tvTag]
            item["name"] = names[tvTag]
            item["type"] = self.Type[lindex]
            item["app"] = "TENCENT"
            yield item

    #ok
    def ParseMoviePage(self, response):

        item = response.meta["item"]
        lindex = response.meta["index"]
        reshtml = response.text

        item["uid"] = re.search(r'param\[\'tvid\'\] = "(.*?)";',reshtml).group(1)
        item["hid"] = re.search(r'/v_(.*?).html"', str(response.url)).group(1)
        item["name"] = item["title"]
        item["type"] = self.Type[lindex]
        item["app"] = "TENCENT"

        yield item



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
