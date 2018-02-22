# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LagouItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # title = scrapy.Field()
    # link = scrapy.Field()
    # desc = scrapy.Field()
    city = scrapy.Field()
    language = scrapy.Field()
    companyId = scrapy.Field()
    companyShortName = scrapy.Field()
    createTime = scrapy.Field()
    positionId = scrapy.Field()
    salary = scrapy.Field()
    workYear = scrapy.Field()
    education = scrapy.Field()
    positionName = scrapy.Field()
    companySize = scrapy.Field()
