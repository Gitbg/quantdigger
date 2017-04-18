# -*- coding: UTF-8 -*-
import scrapy

class xd_stocks_spider(scrapy.Spider):
    name = "xd_stocks"

    def start_requests(self):
        url = "http://www.cninfo.com.cn/information/memo/jyts_more.jsp?datePara="
        xd_date = getattr(self, 'xd_date', None)
        if xd_date is not None:
            url = url + xd_date
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        stocks = []
        item = response.xpath(u'//td[contains(text(), "分红转增除权除息日")]')
        codes = item.xpath('../following-sibling::tr[1]/td[1]/table[1]/tr[1]/input/@value')
        for code in codes.extract():
            stocks.append(code[-6:])
        print stocks
        yield {
            'xd_stocks': [stock for stock in stocks]
        }
