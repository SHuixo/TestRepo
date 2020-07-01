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
		"""京东"""
		urls = response.xpath('//li[@class="gl-item"]/div/div[@class="p-name p-name-type-2"]/a')
		for url in urls:
			item = JDSItem()
			item['keyword'] = self.keyword
			url = url.xpath('@href').extract()
			item['link']  = response.urljoin(url[0])# 商品链接

			for link in url:
				url = response.urljoin(link)
				yield scrapy.Request(url=url, meta={'meta': item}, callback=self.parseItemDetails)

	def parseItemDetails(self, response):
		item = response.meta["meta"]
		#获取商品的id，构建评论url
		item["id"] = item["link"].split('/')[-1].split('.')[0]
		#print("获得商品的品牌")
		item_mark = str(response.xpath('string(//*[@id="crumb-wrap"]/div/div[1]/div[7]/a)').extract()[0])
		item_mark += str(response.xpath('string(//*[@id="crumb-wrap"]/div/div[1]/div[7]/div/div/div[1]/a)').extract()[0])
		item["mark"] = item_mark
		#print("获得商品的名称")
		item["name"] = str(response.xpath('string(//*[@class="sku-name"])').extract()[0]).strip()
		#print("获得产品的颜色")
		item_color = response.xpath('//*[@id="choose-attr-1"]/div[2]//@data-value').extract()
		item_color = ",".join(item_color)
		item["color"] = item_color
		#print("获得产品的型号")
		item_type = response.xpath('//*[@id="choose-attr-2"]/div[2]//@data-value').extract()
		item_type = ",".join(item_type)
		item["type"] = item_type
		#获得产品价格
		price_url = "https://p.3.cn/prices/mgets?callback=jQuery8876824&skuIds=" + str(item["id"])
		price = requests.get(price_url).text
		money = re.findall(r'\"p\"\:\"(.*?)\"}]\)', price)
		item['price'] = money[0]

		commenturl = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds=" + str(item["id"])
		comres = requests.get(commenturl).text
		datares = json.loads(comres)
		##累计评论数
		comnumstr = datares['CommentsCount'][0]['CommentCountStr']
		item['ccountstr'] = comnumstr

		yield item
