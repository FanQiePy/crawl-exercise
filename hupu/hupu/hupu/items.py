# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HupuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    block = scrapy.Field()
    reply_num = scrapy.Field()
    date = scrapy.Field()
    pass


class HupuUserItem(scrapy.Item):
    user_id = scrapy.Field()
    gender = scrapy.Field()
    city = scrapy.Field()
    grade = scrapy.Field()
    online_time = scrapy.Field()
    join_time = scrapy.Field()
    pass
