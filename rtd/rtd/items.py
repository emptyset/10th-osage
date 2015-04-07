# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.contrib.loader.processor import TakeFirst
import scrapy

class RtdItem(scrapy.Item):
    # MH (Monday-Thursday), F (Friday), S (Saturday), SH (Sunday/Holiday)
    day = scrapy.Field()
    # C, D, E, F, H, or W
    route = scrapy.Field()

    # departing from 10th/Osage (if route is W, Auraria West)
    depart_time = scrapy.Field()
    # arriving at Auraria West (if route is W, Golden)
    arrive_time = scrapy.Field()

    pass
