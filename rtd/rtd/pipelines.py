# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem

class RtdWestPipeline(object):
    def process_item(self, item, spider):
        #print '-- pipeline --'
        
        id = item['id']
        depart_time = item['depart_time']
        #print id, depart_time

        if id:
            return item
        else:
            raise DropItem("%s" % item)

