# -*- coding: utf-8 -*-
#使用selenium解决动态加载数据抓取
import requests
from YKScrapy.items import YkscrapyItem
import json
import scrapy
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

class YKSpider(scrapy.Spider):
	name = 'youku'

	def __init__(self):
		#chrome浏览器
		self.timeout = 30
		self.prefs = {"profile.managed_default_content_settings.images": 2}
		self.browser_options = webdriver.ChromeOptions()
		self.browser_options.add_experimental_option("prefs", self.prefs)
		self.browser_options.add_argument('lang=zh_CN.utf-8')
		self.browser = webdriver.Chrome(chrome_options=self.browser_options)
		self.browser.set_page_load_timeout(self.timeout)
		self.SPAGES = 2
		self.KEY_WORDS = [
		"智能音箱","家庭私有云网盘","家庭投影仪","故事机","电视果","智能电视","智能机器人","VR一体机","VR眼睛",
		"智能遥控","智能插座","智能开关","智能台灯","智能球泡灯","窗帘控制器",
		"智能手环","智能体脂秤","智能马桶盖","空气净化器","智能体温计","香薰助眠灯","加湿器","空气净化器","净水器","PM2.5检测仪",
		"智能摄像头","安防套件","智能门锁","智能猫眼","智能门铃","智能摄像头"
		]
		self.PSORTS = ["0","3","4"]
		self.keyword = '智能音箱'
		self.psort = "0" ##0：默认综合排序 3：销量，4：评论数

	def closed(self, spider):
		print("关闭Chrome")
		self.browser.close()

	def start_requests(self):

		#for self.psort in self.PSORTS:
		for self.keyword in self.KEY_WORDS:
			for spage in range(1, self.SPAGES, 2):

				jdurl = 'https://search.jd.com/Search?keyword='+ self.keyword +'&enc=utf-8&psort=0&page='+str(spage)
				yield scrapy.Request(url=jdurl, callback=self.parse)

	def parse(self, response):

				yield scrapy.Request(url=url, meta={'meta': item}, callback=self.parseItemDetails)

	def parseItemDetails(self, response):


		yield item
