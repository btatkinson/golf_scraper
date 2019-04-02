# -*- coding: utf-8 -*-
import scrapy
import datetime

from golf_scraper.items import Tournament
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response
from golf_scraper.settings import *

class SchedulesSpider(scrapy.Spider):
    name = 'schedules'
    allowed_domains = ['pgatour.com','europeantour.com']
    start_urls = ['http://pgatour.com/']

    def __init__(self, *args, **kwargs):
        super(SchedulesSpider, self).__init__(*args, **kwargs)
        this_year = datetime.date.today().year
        print('\n\nCollecting PGA schedules from '+str(PGA_START_YEAR) + ' to ' + str(this_year))
        print('Collecting Euro schedules from '+str(EURO_START_YEAR) + ' to ' + str(this_year))
        print('Collecting Web schedules from '+str(WEB_START_YEAR) + ' to ' + str(this_year)+'\n\n')

    def start_requests(self):
        urls = [
            '',
        ]
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):
        pass
