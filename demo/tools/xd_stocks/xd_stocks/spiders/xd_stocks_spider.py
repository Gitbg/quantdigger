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
        xd_stocks  = []
        fp_stocks  = []
        new_stocks = []

        xd_item = response.xpath(u'//td[contains(text(), "分红转增除权除息日")]')
        xd_codes = xd_item.xpath('../following-sibling::tr[1]/td[1]/table[1]/tr/input/@value')
        for code in xd_codes.extract():
            xd_stocks.append(code[-6:])

        new_item = response.xpath(u'//td[contains(text(), "首发新股上市日")]')
        new_codes = new_item.xpath('../following-sibling::tr[1]/td[1]/table[1]/tr/input/@value')
        for code in new_codes.extract():
            new_stocks.append(code[-6:])

        fp_item = response.xpath(u'//td[contains(text(), "复牌日")]')
        fp_codes = fp_item.xpath('../following-sibling::tr[1]/td[1]/table[1]/tr/td/a/@onclick')
        for code in fp_codes.extract():
            fp_stocks.append(code[24:30])

        yield {
            'xd_stocks': xd_stocks,
            'fp_stocks': fp_stocks,
            'new_stocks': new_stocks
        }
