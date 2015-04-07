import scrapy

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from rtd.items import RtdItem

class RtdWestSpider(scrapy.Spider):
    name = "rtd"
    allowed_domains = ["rtd-denver.com"]
    start_urls = [
            # C/D (MH)
            "http://www3.rtd-denver.com/schedules/getSchedule.action?runboardId=151&routeId=101&routeType=2&direction=N-Bound&serviceType=4&branch=&branch=&branch=&branch=&lineName=SW&branch=&colStart=8&colEnd=9&rowStart=0&rowEnd=0",
            # E/F/H (MH)
            "http://www3.rtd-denver.com/schedules/getSchedule.action?runboardId=151&routeId=101&routeType=2&direction=N-Bound&serviceType=4&branch=&branch=&lineName=SE&branch=&colStart=16&colEnd=17&rowStart=0&rowEnd=0",
            # W (MH)
            "http://www3.rtd-denver.com/schedules/getSchedule.action?runboardId=151&routeId=103&routeType=2&direction=W-Bound&serviceType=4&branch=W&branch=W&branch=W&branch=W&lineName=W&branch=W&colStart=4&colEnd=15&rowStart=0&rowEnd=0"
        ]

    def parse(self, response):
        for sel in response.xpath('//tr'):
            loader = ItemLoader(item = RtdItem(), selector = sel)
            loader.default_output_processor = TakeFirst()

            loader.add_value('day', 'MH')
            loader.add_xpath('route', 'th/a/text()')
            loader.add_xpath('depart_time', 'td[1]/text()')
            loader.add_xpath('arrive_time', 'td[2]/text()')
            yield loader.load_item()

