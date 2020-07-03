# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#
# class YkscrapyItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name= scrapy.Field()
#     # pass


class YKItem(scrapy.Item):
    uid = scrapy.Field()   # 视频url请求id
    pid = scrapy.Field()   # 视频系列id
    hid = scrapy.Field()   # 视频隐藏id
    title = scrapy.Field()   # 视频标题名称
    name = scrapy.Field()   # 视频剧集名称
    actor = scrapy.Field()   # 视频演员
    category = scrapy.Field()   # 视频标签
    type = scrapy.Field()   # 视频种类
    app = scrapy.Field()   # app（网站）名称
