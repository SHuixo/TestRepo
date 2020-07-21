# -*- coding: utf-8 -*-
# 使用selenium解决动态加载数据抓取
import copy
import csv
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
        self.TypeMap = {'电视剧':0, '电影':1, '综艺':2, '动漫':3,"纪录片":4}
        self.Areas = [utils.TVAreas,utils.MovieAreas,utils.ShowAreas,utils.AnimalAreas,utils.VlogAreas]
        self.Maps = {"channel_id=2": 0, "channel_id=1": 1, "channel_id=6": 2, "channel_id=4": 3, "channel_id=3":4}
        self.Func = [self.ParseTvPage, self.ParseMoviePage, self.ParseShowPage, self.ParseAnimalPage,self.ParseVlogPage]
        self.SWITCH = False  #用于从网站获取内容(True)和从本地文件(False)获取内容的切换。
        self.IUrl = "https://www.iqiyi.com/v_{ID}.html"
        self.File = r"./checkIQIYI.txt"

    def start_requests(self):
        if self.SWITCH:
            for reqUrl in utils.IQIYIUrls:
                logging.warning("Start reqUrl {url}".format(url=reqUrl))
                for mode in utils.IQIYIModes:
                    logging.warning("Start reqUrl ：{url} | mode： {mode}".format(url=reqUrl,mode=mode))
                    lindex = [self.Maps[key] for key in self.Maps if key in reqUrl][0]
                    for iarea in self.Areas[lindex]:
                        logging.warning("Start reqUrl :{url}| mode：{mode} | iarea : {iarea}".format(url=reqUrl,mode=mode,iarea=iarea))
                        for lpage in range(1, 20):
                            logging.warning("Start reqUrl :{url}| mode：{mode} | iarea : {iarea} | page : {page}".format(url=reqUrl,mode=mode,iarea=iarea,page=lpage))
                            yield scrapy.Request(url=reqUrl.format(mode=mode,iarea=iarea,lPage=lpage), meta=copy.deepcopy({"index":lindex}),callback= self.getHtml)
                        logging.warning("finish all page")
                    logging.warning("finish all area")
                logging.warning("finish all mode")
            logging.warning("Finish all reqUrl")
        else:
            #从本地文件读取入手！！
            with open(self.File) as csvfile:
                lines = csv.reader(csvfile)
                for line in lines:
                    logging.warning("Start spider 读取到 line= {}".format(line[0]))
                    yield scrapy.Request(url=self.IUrl.format(ID=line[0]), meta=copy.deepcopy({"ID":line[0]}),callback=self.getOtherItem,dont_filter=True)
                logging.warning("读取完毕！！")

    def getOtherItem(self,response):

        if "抱歉" in  str(response.xpath(r'string(//*[@id="block-B"]/div/div/div[2]/div/p)').extract_first()):
            yield None
        reshtml = response.text
        categoryName = re.search(r'"categoryName":"(.*?)",',reshtml).group(1)
        item = IQIYItem()
        item["app"] = "IQIYI"
        item["actor"] = None
        item["pid"] = re.findall(r'param\[\'albumid\'\] = "(.*?)";',reshtml)[0]
        item["title"] = self.strRegex.sub('',re.search(r'"albumName":"(.*?)",',reshtml).group(1))
        try:
            item["category"] = self.strRegex.sub('',re.search(r'"categories":"(.*?)",',reshtml).group(1))
        except:
            item["category"] = None
        indexl = [self.TypeMap[key] for key in self.TypeMap if key in categoryName]
        if indexl != []:
            lindex = indexl[0]
            yield scrapy.Request(url=response.url,meta=copy.deepcopy({"item":item,"index":lindex}),callback= self.Func[lindex],dont_filter=True)
        else:
            allData = re.findall(r'initialized-data=\'\[(.*)?\]\'>',reshtml)
            item["type"] = self.strRegex.sub('',categoryName)
            if [] == allData:
                allData = re.findall(r'initialized-data="\[(.*)?\]">',reshtml)
            if [] == allData:
                item["uid"] = re.findall(r'param\[\'tvid\'\] = "(.*?)";',reshtml)[0]
                item["name"] = re.findall(r'"tvName":"(.*?)",',reshtml)[0]
                item["hid"] = response.meta["ID"]
                yield item
            else:
                allData = allData[0]
                if "albumId&quot;:" in allData:
                    tvIds = re.findall(r'tvId&quot;:(.*?),',allData)
                    names = re.findall(r'name&quot;:&quot;(.*?)&quot;,',allData)
                elif 'albumId":' in allData:
                    tvIds = re.findall(r'tvId":(.*?),',allData)
                    names = re.findall(r'name":"(.*?)",',allData)
                for aindex, tvId in enumerate(tvIds):
                    item["uid"] = tvId
                    item["name"] = names[aindex]
                    item["hid"] = None
                    yield item


    def getHtml(self,response):
        reshtml = response.text
        if re.findall(r'"list":(.*?),', reshtml) == []:
            yield None
        else:
            lindex = response.meta["index"]
            playUrls = [url.split('"')[0] for url in re.findall(r'playUrl":"(.*?)",', reshtml)]
            albumIds = re.findall(r'"albumId":(.*?),', reshtml)
            titles = re.findall(r'"title":"(.*?)",', reshtml)
            categories = re.findall(r'"categories":(.*?),', reshtml)
            actors = re.findall(r'"people":{(.*?)}', reshtml)
            for tag, playurl in enumerate(playUrls):
                item = IQIYItem()
                item["pid"] = albumIds[tag]
                item["title"] = self.strRegex.sub('',titles[tag])
                item["category"] = self.strRegex.sub('',categories[tag])
                item["actor"] = self.strRegex.sub('',str(re.findall(r'"name":"(.*?)"}',str(actors[tag]))))
                item["app"] = "IQIYI"
                yield scrapy.Request(url=playurl,meta=copy.deepcopy({"item":item,"index":lindex}),callback= self.Func[lindex])


    def ParseTvPage(self, response):

        item = response.meta["item"]
        lindex = response.meta["index"]
        ##获取该电视剧所有集数的属性信息
        headers = {"User-Agent": random.choice(utils.USER_AGENTS)}
        PageUrl="https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={aid}&page={page}&size=30"
        reshtml = requests.get(PageUrl.format(aid=item["pid"],page="1"), headers=headers).text
        tvIds = re.findall(r'tvId":(.*?),',reshtml)
        hids = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',reshtml)))
        names = re.findall(r'name":"(.*?)",',str(re.findall(r'"tvId":(.*?)"playUrl"',reshtml)))
        if len(hids) != len(tvIds):
            hids = [hid.split('/')[-1] for hid in re.findall(r'/(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',reshtml)))]
        rp =  re.findall(r'page":(.*?),',reshtml)
        if rp is not None or rp != []:
            pages = (int)(rp[0])
        else:
            pages = 1
        if pages > 1:
            for page in range(2,pages+1):
                reshtml = requests.get(PageUrl.format(aid=item["pid"], page=page), headers=headers).text
                tvtmp = re.findall(r'tvId":(.*?),',reshtml)
                htmp = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',reshtml)))
                nametmp = re.findall(r'name":"(.*?)",',str(re.findall(r'"tvId":(.*?)"playUrl"',reshtml)))
                if len(htmp) != len(tvtmp):
                    htmp = [hid.split('/')[-1] for hid in re.findall(r'/(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',reshtml)))]
                tvIds.extend(tvtmp)
                hids.extend(htmp)
                names.extend(nametmp)

        for tvTag, tvid in enumerate(tvIds):
            item["uid"] = tvid
            item["hid"] = hids[tvTag]
            item["name"] = self.strRegex.sub('',names[tvTag])
            item["type"] = self.Type[lindex]
            yield item

    #ok
    def ParseMoviePage(self, response):

        item = response.meta["item"]
        lindex = response.meta["index"]
        reshtml = response.text

        item["uid"] = re.search(r'param\[\'tvid\'\] = "(.*?)";',reshtml).group(1)
        rse = re.search(r'/v_(.*?).html"', str(response.url))
        if rse is not None:
            item["hid"] = rse.group(1)
        else:
            item["hid"]  = None
        item["name"] = item["title"]
        item["type"] = self.Type[lindex]
        yield item

    ## 综艺类节目，hid不好获取暂时置为None
    def ParseShowPage(self,response):
        item = response.meta["item"]
        lindex = response.meta["index"]
        item["hid"] = None
        item["type"] = self.Type[lindex]
        resSoup = response.text
        allData = re.findall(r'initialized-data=\'\[(.*)?\]\'>',resSoup)
        if [] == allData:
            allData = re.findall(r'initialized-data="\[(.*)?\]">',resSoup)
        if [] == allData:
            item["uid"] = re.findall(r'param\[\'tvid\'\] = "(.*?)";',resSoup)[0]
            item["name"] = re.findall(r'"tvName":"(.*?)",',resSoup)[0]
            yield item
        else:
            allData = allData[0]
            if "albumId&quot;:" in allData:
                tvIds = re.findall(r'tvId&quot;:(.*?),',allData)
                names = re.findall(r'name&quot;:&quot;(.*?)&quot;,',allData)
            elif 'albumId":' in allData:
                tvIds = re.findall(r'tvId":(.*?),',allData)
                names = re.findall(r'name":"(.*?)",',allData)

            for aindex, tvId in enumerate(tvIds):

                item["uid"] = tvId
                item["name"] = names[aindex]
                yield item

    def ParseAnimalPage(self,response):
        item = response.meta["item"]
        lindex = response.meta["index"]
        headers = {"User-Agent": random.choice(utils.USER_AGENTS)}
        resSoup = response.text
        item["type"] = self.Type[lindex]
        if '0' == item["pid"]:
            item["uid"] = re.findall(r'param\[\'tvid\'\] = "(.*?)";',resSoup)[0]
            try:
                item["hid"] = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))[0]
            except IndexError as e:
                item["hid"] = None
            item["name"] = re.findall(r'meta content="(.*?)" property="og:title"/>',resSoup)[0]
            yield item
        else:
            PageUrl="https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={aid}&page={page}&size=30"
            resSoup = requests.get(PageUrl.format(aid=item["pid"],page="1"), headers=headers).text
            tvIds = re.findall(r'tvId":(.*?),',resSoup)
            hids = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))
            names = re.findall(r'"name":"(.*?)"',str(re.findall(r'"tvId":(.*?)"playUrl"',resSoup)))
            if len(hids) != len(tvIds):
                hids = [hid.split('/')[-1] for hid in re.findall(r'/(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))]
            rp =  re.findall(r'page":(.*?),',resSoup)
            if rp is not None:
                pages = (int)(rp[0])
            else:
                pages = 1
            if pages > 1:
                for page in range(2,pages+1):
                    resSoup = requests.get(PageUrl.format(aid=item["pid"], page=page), headers=headers).text
                    ttmp = re.findall(r'tvId":(.*?),',resSoup)
                    htmp = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))
                    names.extend(re.findall(r'"name":"(.*?)"',str(re.findall(r'"tvId":(.*?)"playUrl"',resSoup))))
                    if len(htmp) != len(ttmp):
                        htmp = [hid.split('/')[-1] for hid in re.findall(r'/(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))]
                    tvIds.extend(ttmp)
                    hids.extend(htmp)

            for anatag, tvid in enumerate(tvIds):
                item["uid"] = tvid
                item["hid"] = hids[anatag]
                item["name"] = names[anatag]
                yield item

    def ParseVlogPage(self,response):

        item = response.meta["item"]
        lindex = response.meta["index"]
        item["type"] = self.Type[lindex]
        headers = {"User-Agent": random.choice(utils.USER_AGENTS)}
        PageUrl="https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={aid}&page={page}&size=30"
        resSoup = requests.get(PageUrl.format(aid=item["pid"],page="1"), headers=headers).text
        tvIds = re.findall(r'tvId":(.*?),',resSoup)
        hids = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))
        names = re.findall(r'"name":"(.*?)"',str(re.findall(r'"tvId":(.*?)"playUrl"',resSoup)))
        if len(hids) != len(tvIds):
            hids = [hid.split('/')[-1] for hid in re.findall(r'/(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))]
        rp =  re.findall(r'page":(.*?),',resSoup)
        if rp != []:
            pages = (int)(rp[0])
        else:
            pages = 1
        if pages > 1:
            for page in range(2,pages+1):
                resSoup = requests.get(PageUrl.format(aid=item["pid"], page=page), headers=headers).text
                ttmp = re.findall(r'tvId":(.*?),',resSoup)
                htmp = re.findall(r'/v_(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))
                names.extend(re.findall(r'"name":"(.*?)"',str(re.findall(r'"tvId":(.*?)"playUrl"',resSoup))))
                if len(htmp) != len(ttmp):
                    htmp = [hid.split('/')[-1] for hid in re.findall(r'/(.*?).html"',str(re.findall(r'"playUrl":(.*?),"issueTime',resSoup)))]
                tvIds.extend(ttmp)
                hids.extend(htmp)

        for anatag, tvid in enumerate(tvIds):
            item["uid"] = tvid
            item["hid"] = hids[anatag]
            item["name"] = names[anatag]
            yield item
