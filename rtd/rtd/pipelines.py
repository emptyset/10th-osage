# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import sqlite3

from scrapy.exceptions import CloseSpider
from scrapy.exceptions import DropItem

class RtdPipeline(object):

    def open_spider(self, spider):
        try:
            self.db_connection = sqlite3.connect('rtd.db')
            cursor = self.db_connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS schedule")
            cursor.execute("CREATE TABLE schedule(direction TEXT, day TEXT, route TEXT, depart_time INT, arrive_time INT)")
        except sqlite3.Error, e:
            raise CloseSpider(e.args[0])

    def close_spider(self, spider):
        if self.db_connection:
            self.db_connection.close()

    def process_item(self, item, spider):
        # print '-- enter pipeline'

        # if route is W, then
        #   depart_time is departure from Auraria West
        #   arrive_time is arrival at Golden
        # else
        #   depart_time is departure from 10th/Osage
        #   arrive_time is arrival at Auraria West
       
        direction = item['direction']
        day = item['day']
        route = item['route']
        depart_time = self.convert_time(item['depart_time'])
        arrive_time = self.convert_time(item['arrive_time'])

        # validations/tests
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

            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO schedule VALUES (?, ?, ?, ?, ?)", (direction, day, route, depart_time, arrive_time))
            self.db_connection.commit()
            
            # print route, item['depart_time'], item['arrive_time']
            return item
        else:
            # print '-- drop item'
            # print '-- exit pipeline'
            raise DropItem("%s" % item)

    # TODO: definite move into common module
    def convert_time(self, time):
        if time == '--':
            return None

        am_pm = time[len(time) - 1]
        time = time[:-1]
        if (am_pm == 'A'):
            if (len(time) == 4 and time[:2] == '12'):
                time = int(time) - 1200
        else:
            if (len(time) == 3 or (len(time) == 4 and time[:2] != '12')):
                time = 1200 + int(time)

        return int(time)
