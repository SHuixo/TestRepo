# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import copy
import MySQLdb.cursors
from scrapy.conf import settings
from twisted.enterprise import adbapi

class YkscrapyPipeline(object):
    def process_item(self, item, spider):
        return item

class MySQLPipeline(object):

    def __init__(self):
        self.dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **self.dbparams)  # **表示将字典扩展为关键字参数,

    ## pipeline默认调用
    def process_item(self, item, spider):
        asyncitem = copy.deepcopy(item)
        query = self.dbpool.runInteraction(self._conditional_insert, asyncitem)  # 调用插入的方法
        query.addErrback(self._handle_error, asyncitem, spider)  # 调用异常处理方法
        return asyncitem

    # 写入数据库中(设置了unique索引，保证id号的唯一性)
    def _conditional_insert(self, tx, item):
        sql = "insert ignore into youkusrc(crawler_app_id1,crawler_app_id2,crawler_app_id3,crawler_name,crawler_name2,crawler_actor,crawler_property,crawler_content_type,app_from) " \
              "values(%s,%s, %s,%s,%s,%s,%s,%s,%s)"
        params = (item["uid"], item["pid"],item["hid"], item["title"],item["name"], item["actor"],item["category"],item['type'],item['app'])
        tx.execute(sql, params)
        print("# database operation sunccess ! ")

    # 错误处理方法
    def _handle_error(self, failue, item, spider):
        print('* * * * * * *  database operation exception ! ! * * * * * * *')
        print(failue)
