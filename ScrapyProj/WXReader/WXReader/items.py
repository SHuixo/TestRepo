# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WxreaderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class WXItem(scrapy.Item):
    uid = scrapy.Field()   # 图书唯一标志id
    classify = scrapy.Field() #图书分类
    type = scrapy.Field()   # 图书类型
    name = scrapy.Field()   # 图书名称
    author = scrapy.Field()   # 图书作者
    publish = scrapy.Field()   # 出版社
    ptime = scrapy.Field()    #出版时间
    price = scrapy.Field()    #图书价格
    isbn = scrapy.Field()     #图书isbn
    country = scrapy.Field()  #图书国籍
    label = scrapy.Field()   # 图书标签
    score = scrapy.Field()   #图书评分
    commNum = scrapy.Field() #评论人数
    readNum = scrapy.Field()  #阅读人数
    collNum = scrapy.Field()  #收藏数
    app = scrapy.Field()   # app（网站）名称
