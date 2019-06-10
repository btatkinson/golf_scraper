# -*- coding: utf-8 -*-
import scrapy
import datetime
import pandas as pd
import numpy as np

from scrapy_splash import SplashRequest
from scrapy.selector import Selector

from golf_scraper.items import Tournament
from scrapy.shell import inspect_response
from golf_scraper.settings import *

class SchedulesSpider(scrapy.Spider):
    name = 'schedules'
    allowed_domains = ['pgatour.com','europeantour.com']
    start_urls = ['http://pgatour.com/']
    custom_settings = {
        'ITEM_PIPELINES': {
            'golf_scraper.pipelines.SchedulePipeline': 400
        }
    }

    def __init__(self, *args, **kwargs):
        super(SchedulesSpider, self).__init__(*args, **kwargs)
        self.this_year = datetime.date.today().year

    def start_requests(self):

        # generate URLS
        pga_urls = []
        euro_urls = []
        web_urls = []

        pga_years = list(range(PGA_START_YEAR, (self.this_year+1)))
        euro_years = list(range(EURO_START_YEAR, (self.this_year+1)))
        web_years = list(range(WEB_START_YEAR, (self.this_year+1)))

        sched = None
        try:
            sched = pd.read_csv('./sched.csv')
        except:
            pass

        if sched is not None:
            print(sched)
            # already collected years
            ac_pga = sched.loc[sched.tour=='PGA']
            ac_pga = list(ac_pga.season.unique())
            ac_euro = sched.loc[sched.tour=='Euro']
            ac_euro = list(ac_euro.season.unique())
            ac_web = sched.loc[sched.tour=='Web']
            ac_web = list(ac_web.season.unique())

            # turn into ints
            ac_pga = list(map(int, ac_pga))
            ac_euro = list(map(int, ac_euro))
            ac_web = list(map(int, ac_web))

            # years not collected
            pga_years = list(set(pga_years) - set(ac_pga))
            euro_years = list(set(euro_years) - set(ac_euro))
            web_years = list(set(web_years) - set(ac_web))

        print("PGA years to collect: ", pga_years)
        print("Euro years to collect: ", euro_years)
        print("Web years to collect: ", web_years)

        # for pga and web, current year is treated differently
        if self.this_year in pga_years:
            pga_urls.append((self.this_year,'https://www.pgatour.com/tournaments/schedule.html'))
            pga_years.remove(self.this_year)
        if self.this_year in web_years:
            web_urls.append((self.this_year,'https://www.pgatour.com/webcom/tournaments/schedule.html'))
            web_years.remove(self.this_year)

        # append tuples so year info is passed
        for yr in pga_years:
            pga_urls.append((yr,'https://www.pgatour.com/tournaments/schedule.history.'+str(yr)+'.html'))

        for yr in euro_years:
            euro_urls.append((yr,'http://www.europeantour.com/europeantour/tournament/Season='+str(yr)+'/index_full.html'))

        for yr in web_years:
            web_urls.append((yr,'https://www.pgatour.com/webcom/tournaments/schedule.history.'+str(yr)+'.html'))

        # testing
        # pga_urls = pga_urls[:1]
        # euro_urls = euro_urls[:1]
        # web_urls = web_urls[:1]

        for url in pga_urls:
            sr = SplashRequest(url=url[1], args={'timeout': 90,'wait':1}, callback=self.pga_parse)
            sr.meta['season'] = url[0]
            yield sr

        for url in web_urls:
            sr = SplashRequest(url=url[1], args={'timeout': 90,'wait':1}, callback=self.web_parse)
            sr.meta['season'] = url[0]
            yield sr

        for url in euro_urls:
            sr = SplashRequest(url=url[1], args={'timeout': 90,'wait':1}, callback=self.euro_parse)
            sr.meta['season'] = url[0]
            yield sr

    def pga_parse(self, response):
        # inspect_response(response,self)
        trn = Tournament()
        hxs = Selector(response)
        if response.meta['season'] == self.this_year:
            table = hxs.xpath('//table[@class="table-styled js-table"]')
        else:
            table = hxs.xpath('//table[@class="table-styled js-table schedule-history-table"]')

        rows = table.css('tr')

        # has it been january yet? (some tournaments are from the prior calendar year)
        jan = False
        for row in rows:
            date = row.css('span::text').getall()
            month = ''.join(filter(str.isalpha, date))
            if "Jan" in month:
                jan = True
            if jan is True:
                trn['year'] = response.meta['season']
            else:
                trn['year'] = response.meta['season'] - 1
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
        trn = Tournament()
        hxs = Selector(response)
        table = hxs.css('[id=includeSchedule]')
        rows = table.css('tr')
        # has it been january yet? (some tournaments are from the prior calendar year)
        jan = False
        for row in rows:
            cells = row.css('td')

            trn['tour'] = "Euro"
            trn['season'] = response.meta['season']
            trn['start_date'] = cells[1].css('::text').get()
            month = ''.join(filter(str.isalpha, trn['start_date']))
            if "Jan" in month:
                jan = True
            if jan is True:
                trn['year'] = response.meta['season']
            else:
                trn['year'] = response.meta['season'] - 1
            trn['end_date'] = cells[2].css('::text').get()
            trn['name'] = cells[4].css('a::text').get()
            trn['location'] = cells[4].css('li::text').get()
            trn['link'] = row.css('a::attr(href)').get()

            yield trn

    def web_parse(self, response):
        trn = Tournament()
        hxs = Selector(response)
        if response.meta['season'] == self.this_year:
            table = hxs.xpath('//table[@class="table-styled js-table"]')
        else:
            table = hxs.xpath('//table[@class="table-styled js-table schedule-history-table"]')
        rows = table.css('tr')
        # has it been january yet? (some tournaments are from the prior calendar year)
        jan = False
        for row in rows:
            cells = row.css('td')
            if len(cells) < 3:
                continue
            trn['tour'] = "Web"
            trn['season'] = response.meta['season']
            # date
            l_date = cells[0].css('span::text').getall()
            trn['start_date'] = " ".join([x.strip() for x in l_date])
            month = ''.join(filter(str.isalpha, trn['start_date']))
            if "Jan" in month:
                jan = True
            if jan is True:
                trn['year'] = response.meta['season']
            else:
                trn['year'] = response.meta['season'] - 1
            l_info = cells[1].css('::text').getall()
            # strip whitespace
            l_info = [x.strip() for x in l_info]
            info = [x for x in l_info if len(x) > 0]
            trn['name'] = info[0]
            trn['location'] = info[1]

            try:
                trn['link'] = row.css('a::attr(href)').get()
            except:
                trn['link'] = "Not Available"

            yield trn
