# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import numpy as np
import datetime

from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
from scrapy.selector import Selector

from golf_scraper.items import Player_Tournament

import sys
sys.path.insert(0,'./golf_scraper/spiders/helpers/')
from scores_helper import *

class Tournament(object):
    """docstring for Tournament."""
    def __init__(self, row):
        super(Tournament, self).__init__()
        self.end_date = row[0]
        self.link = row[1]
        self.location = row[2]
        self.name = row[3]
        self.season = row[4]
        self.start_date = row[5]
        self.tour = row[6]
        self.year = row[7]

class ScoresSpider(scrapy.Spider):
    name = 'scores'
    allowed_domains = ['pgatour.com']
    start_urls = ['http://pgatour.com/','europeantour.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'golf_scraper.pipelines.ScoresPipeline': 400
        }
    }
    def __init__(self, *args, **kwargs):
        super(ScoresSpider, self).__init__(*args, **kwargs)

    def start_requests(self):

        # load tournaments
        sched = pd.read_csv('./sched.csv')

        # tournament object list
        trns = []
        for index, row in sched.iterrows():
            trn = Tournament(row)
            trns.append(trn)

        # testing
        trns=trns[1799:1800]

        for trn in trns:
            date = datetime.datetime.strptime(trn.end_date, '%b %d %Y').date()
            if date > datetime.datetime.today().date():
                continue
            if trn.tour == 'PGA':
                sr = SplashRequest(url=trn.link, args={'timeout': 90,'wait':1}, callback=self.pga_parse)
            elif trn.tour == 'Euro':
                sr = SplashRequest(url=trn.link, args={'timeout': 90,'wait':1}, callback=self.euro_parse)
            elif trn.tour == 'Web':
                sr = SplashRequest(url=trn.link, args={'timeout': 90,'wait':1}, callback=self.web_parse)
            else:
                continue
            sr.meta['Trn'] = trn
            yield sr

    def pga_parse(self, response):

        hxs = Selector(response)

        # different links have different table classes
        table_found = False
        # for past results
        table = hxs.xpath('//table[@class="table-styled"]')
        if len(table) > 0:
            table_found = True
        # for more current tournaments
        if not table_found:
            table = hxs.xpath('//table[@class="leaderboard"]')
        if len(table) > 0:
            table_found = True
        if table_found:
            tbody = table.xpath('//tbody')
            rows = tbody.css('tr')
            player_rounds = []
            for row in rows:
                cells = row.css('td::text').getall()
                # the last number is never helpful and can mess up the logic
                cells=cells[:-1]
                # use length of cells to figure out where the player rows begin
                row_len = len(cells)
                if row_len >= 3:
                    # check if first cell is name
                    if not any(char.isdigit() for char in cells[0]):
                        plyr_trn = Player_Tournament()
                        plyr_trn['name'] = cells[0].lstrip()
                        plyr_trn['pos'] = cells[1]
                        plyr_trn['R1'] = cells[2]
                        if len(cells) >= 4:
                            # check if round score
                            is_rnd = check_if_round(cells[3])
                            if is_rnd:
                                plyr_trn['R2'] = cells[3]
                        if len(cells) >= 5:
                            is_rnd = check_if_round(cells[4])
                            if is_rnd:
                                plyr_trn['R3'] = cells[4]
                        if len(cells) >= 6:
                            is_rnd = check_if_round(cells[5])
                            if is_rnd:
                                plyr_trn['R4'] = cells[5]

                        plyr_trn['tournament'] = response.meta['Trn'].name
                        plyr_trn['season'] = response.meta['Trn'].season
                        plyr_trn['tour'] = response.meta['Trn'].tour
                        plyr_trn['end_date'] = response.meta['Trn'].end_date
                        plyr_trn['start_date'] = response.meta['Trn'].start_date
                        plyr_trn['location'] = response.meta['Trn'].location
                        
                        print(plyr_trn)
                        yield plyr_trn

        else:
            # add tournament to not collected file
            with open('./not_collected.txt') as f:
                trns = [line.rstrip('\n') for line in open('./not_collected.txt')]

            trns.append(response.meta['name'], response.meta['season'])

            with open('./not_collected.txt', 'w') as f:
                for item in trns:
                    f.write("%s\n" % item)
        yield
    def euro_parse(self, response):
        # inspect_response(response,self)
        yield
    def web_parse(self, response):
        # inspect_response(response,self)
        yield
