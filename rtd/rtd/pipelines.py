# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem

class RtdPipeline(object):
    def process_item(self, item, spider):
        # print '-- enter pipeline'

        # if route is W, then
        #   depart_time is departure from Auraria West
        #   arrive_time is arrival at Golden
        # else
        #   depart_time is departure from 10th/Osage
        #   arrive_time is arrival at Auraria West
       
        route = item['route']
        depart_time = self.convert_time(item['depart_time'])
        arrive_time = self.convert_time(item['arrive_time'])

        if depart_time < 0 and depart_time is not None:
            print '!! ERROR depart_time conversion'
            print '%s' % item
            print 'conversion result: %s' % depart_time

        if arrive_time < 0 and arrive_time is not None:
            print '!! ERROR arrive_time conversion'
            print '%s' % item
            print 'conversion result: %s' % arrive_time

        if route in ["C", "D", "E", "F", "H", "W"]:
            # print '-- return item'
            # print '-- exit pipeline'
            item['depart_time'] = depart_time
            item['arrive_time'] = arrive_time
            # print route, item['depart_time'], item['arrive_time']
            return item
        else:
            # print '-- drop item'
            # print '-- exit pipeline'
            raise DropItem("%s" % item)

    def convert_time(self, time):
        if (time == "--"):
            return None 

        # convert the time into an integer to make comparison easier
        # ex. 1225A -> 25
        # ex. 905A -> 905
        # ex. 1225P -> 1225
        # ex. 645P -> 1845
        
        am_pm = time[len(time) - 1]

        if (am_pm == 'A'):
            time = time[:-1]
            if (len(time) == 4 and time[:2] == "12"):
                time = int(time) - 1200
        else: # am_pm == 'P'
            time = time[:-1]
            if (time[:2] != "12"):
                time = 1200 + int(time)

        return int(time)
