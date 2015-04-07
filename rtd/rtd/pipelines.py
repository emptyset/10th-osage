# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem

class RtdPipeline(object):
    def process_item(self, item, spider):
        print '-- enter pipeline'

        # if route is W, then
        #   depart_time is departure from Auraria West
        #   arrive_time is arrival at Golden
        # else
        #   depart_time is departure from 10th/Osage
        #   arrive_time is arrival at Auraria West
       
        route = item['route']
        depart_time = item['depart_time']
        arrive_time = item['arrive_time']
        print route, depart_time, arrive_time

        if route in ["C", "D", "E", "F", "H", "W"]:
            print '-- return item'
            print '-- exit pipeline'
            return item
        else:
            print '-- drop item'
            print '-- exit pipeline'
            raise DropItem("%s" % item)

