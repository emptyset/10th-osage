# -*- coding: utf-8 -*-

# Scrapy settings for rtd project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'rtd'

SPIDER_MODULES = ['rtd.spiders']
NEWSPIDER_MODULE = 'rtd.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'rtd (+http://faysoftware.com)'

ITEM_PIPELINES = {
        'rtd.pipelines.RtdPipeline': 100
        }
