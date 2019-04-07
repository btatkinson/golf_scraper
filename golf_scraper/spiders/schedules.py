# -*- coding: utf-8 -*-
import scrapy
import datetime

from scrapy_splash import SplashRequest
from scrapy.selector import Selector

from golf_scraper.items import Tournament
from scrapy.shell import inspect_response
from golf_scraper.settings import *

class SchedulesSpider(scrapy.Spider):
    name = 'schedules'
    allowed_domains = ['pgatour.com','europeantour.com']
    start_urls = ['http://pgatour.com/']

    def __init__(self, *args, **kwargs):
        super(SchedulesSpider, self).__init__(*args, **kwargs)
        self.this_year = datetime.date.today().year
        print('\n\n')
        if COLLECT['PGA']:
            print('Collecting PGA schedules from '+str(PGA_START_YEAR) + ' to ' + str(self.this_year))
        if COLLECT['Euro']:
            print('Collecting Euro schedules from '+str(EURO_START_YEAR) + ' to ' + str(self.this_year))
        if COLLECT['Web']:
            print('Collecting Web schedules from '+str(WEB_START_YEAR) + ' to ' + str(self.this_year))
        print('\n\n')

    def start_requests(self):
        pga_urls = []
        euro_urls = []
        web_urls = []

        pga_years = list(range(PGA_START_YEAR, self.this_year))
        euro_years = list(range(EURO_START_YEAR, self.this_year))
        web_years = list(range(WEB_START_YEAR, self.this_year))
        # for pga and web, current year is treated differently
        pga_years = pga_years[:-1]
        web_years = web_years[:-1]

        # append tuples so year info is passed
        for yr in pga_years:
            pga_urls.append((yr,'https://www.pgatour.com/tournaments/schedule.history.'+str(yr)+'.html'))
        pga_urls.append((yr,'https://www.pgatour.com/tournaments/schedule.html'))

        for yr in euro_years:
            euro_urls.append('http://www.europeantour.com/europeantour/tournament/Season='+str(yr)+'/index_full.html')

        for yr in web_years:
            web_urls.append('https://www.pgatour.com/webcom/tournaments/schedule.history.'+str(yr)+'.html')
        web_urls.append('https://www.pgatour.com/webcom/tournaments/schedule.html')

        # testing
        pga_urls = pga_urls[:1]

        for url in pga_urls:
            sr = SplashRequest(url=url[1], args={'timeout': 90,'wait':0.5}, callback=self.pga_parse)
            sr.meta['season'] = url[0]
            yield sr

        for url in euro_urls:
            # yield SplashRequest(url=url, callback=self.euro_parse)
            pass

        for url in web_urls:
            # yield SplashRequest(url=url, callback=self.web_parse)
            pass

    def pga_parse(self, response):
        # inspect_response(response,self)
        trn = Tournament()
        hxs = Selector(response)
        table = hxs.xpath('//table[@class="table-styled js-table schedule-history-table"]')
        rows = table.css('tr')
        for row in rows:
            date = row.css('span::text').getall()
            name = row.css('.js-tournament-name::text').get()
            info = row.css('.tournament-text::text').getall()
            try:
                link = row.css('a::attr(href)').get()
            except:
                link = "Not Available"

            if len(date) <= 0:
                continue
            elif date is None:
                continue
            else:
                trn["start_date"] = date
                trn["name"] = name
                trn["tour"] = "PGA"
                trn["location"] = info
                trn["season"] = response.meta['season']
                trn["link"] = link
            yield trn


    def euro_parse(self, response):
        pass

    def web_parse(self, response):
        pass
