import scrapy


class MGSpider(scrapy.Spider):
    ##必须将selenium包装成移动端设备，才可获取数据！（难度中）
    name = 'MGReader'

    def __init__(self):
        pass

    def start_requests(self):
        pass
