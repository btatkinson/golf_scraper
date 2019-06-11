# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Tournament(scrapy.Item):
    season = scrapy.Field()
    # some tournaments are in a different year than the "season"
    year = scrapy.Field()
    tour = scrapy.Field()
    name = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    location = scrapy.Field()
    link = scrapy.Field()

class Player_Tournament(scrapy.Item):
    name = scrapy.Field()
    pos = scrapy.Field()
    R1 = scrapy.Field()
    R2 = scrapy.Field()
    R3 = scrapy.Field()
    R4 = scrapy.Field()
    tournament = scrapy.Field()
    season = scrapy.Field()
    tour = scrapy.Field()
    location = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
