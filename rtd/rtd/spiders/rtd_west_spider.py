import scrapy

from rtd.items import RtdItem

class RtdWestSpider(scrapy.Spider):
    name = "rtd"
    allowed_domains = ["rtd-denver.com"]
    start_urls = [
            "http://www3.rtd-denver.com/schedules/getSchedule.action?runboardId=151&routeId=103&routeType=2&branch=W&lineName=W&direction=W-Bound&serviceType=5"
        ]

    def parse(self, response):
        for sel in response.xpath('//td[starts-with(@id, "td")]'):
            item = RtdItem()
            item['id'] = sel.xpath('@id').re(r'^td\d+-4$')
            item['depart_time'] = sel.xpath("text()").extract()
            yield item
