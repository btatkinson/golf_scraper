# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Tournament(scrapy.Item):
    # define the fields for your item here like:
    season = scrapy.Field()
    tour = scrapy.Field()
    name = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    location = scrapy.Field()
    link = scrapy.Field()
