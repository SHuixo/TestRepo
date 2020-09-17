import scrapy


class MGSpider(scrapy.Spider):
    ##必须将selenium包装成移动端设备，才可获取数据！
    #此脚本尝试pc端解析，不需要配合selenium！！
    name = 'MGReaderPC'

    def __init__(self):
        pass

    def start_requests(self):
        pass
