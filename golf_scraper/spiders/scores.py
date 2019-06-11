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
    allowed_domains = ['pgatour.com','europeantour.com']
    start_urls = ['http://pgatour.com/','europeantour.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'golf_scraper.pipelines.ScoresPipeline': 400
        }
    }

    def __init__(self, *args, **kwargs):
        super(ScoresSpider, self).__init__(*args, **kwargs)

    def check_to_filter(self, trn):
        should_filter = False

        if 'Match Play' in trn.name:
            should_filter = True

        if 'Ryder Cup' in trn.name:
            should_filter = True

        if trn.tour == 'Web':
            should_filter = True

        return should_filter

    def start_requests(self):

        # load tournaments
        sched = pd.read_csv('./sched.csv')

        # tournament object list
        trns = []
        for index, row in sched.iterrows():
            trn = Tournament(row)
            trns.append(trn)

        # testing
        trns=trns[:50]
        for trn in trns:
            print(trn.link)

        for trn in trns:
            date = datetime.datetime.strptime(trn.end_date, '%b %d %Y').date()
            if date > datetime.datetime.today().date():
                continue

            # check if it matches criteria to throw out
            should_filter = self.check_to_filter(trn)
            if should_filter:
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

                        # can't access response meta in item pipeline, this is hacky solution
                        yield plyr_trn

        yield


    def euro_parse(self, response):
        table_found = False
        # for newer tables
        table = response.xpath('//table[@id="results-table"]')
        if len(table) > 0:
            table_found = True

            header = response.xpath('//table[@id="results-table"]/thead/tr')
            header_cells = header.css('th::text').getall()

            r1_idx = header_cells.index('R1')
            try:
                r2_idx = header_cells.index('R2')
            except:
                print("no round 2")
            try:
                r3_idx = header_cells.index('R3')
            except:
                print("no round 3")
            try:
                r4_idx = header_cells.index('R4')
            except:
                print("no round 4")

            rows = response.xpath('//table[@id="results-table"]/tbody//tr')
            for row in rows:
                plyr_trn = Player_Tournament()

                cells = row.css('td::text').getall()
                # remove empty cells
                cells = [x for x in cells if not x.isspace()]
                plyr_trn['name'] = row.css('a *::text')[0].extract()
                plyr_trn['pos'] = cells[0]
                plyr_trn['R1'] = cells[r1_idx]
                if r2_idx:
                    plyr_trn['R2'] = cells[r2_idx]
                if r3_idx:
                    plyr_trn['R3'] = cells[r3_idx]
                if r4_idx:
                    plyr_trn['R4'] = cells[r4_idx]

                plyr_trn['tournament'] = response.meta['Trn'].name
                plyr_trn['season'] = response.meta['Trn'].season
                plyr_trn['tour'] = response.meta['Trn'].tour
                plyr_trn['end_date'] = response.meta['Trn'].end_date
                plyr_trn['start_date'] = response.meta['Trn'].start_date
                plyr_trn['location'] = response.meta['Trn'].location

                yield plyr_trn

        # for older tables
        if not table_found:
            table = response.xpath('//*[@id="leaderboardTable"]')
        if len(table) > 0:
            table_found = True
            plyr_trn = Player_Tournament()
            rows = response.css('ul.dataRow')
            for row in rows:
                try:
                    plyr_trn['name'] = row.css('a *::text')[0].extract()
                except:
                    continue
                cells = row.css('span::text').getall()
                plyr_trn['pos'] = cells[0]
                plyr_trn['R1'] = cells[3]
                plyr_trn['R2'] = cells[4]
                plyr_trn['R3'] = cells[5]
                plyr_trn['R4'] = cells[6]
                plyr_trn['tournament'] = response.meta['Trn'].name
                plyr_trn['season'] = response.meta['Trn'].season
                plyr_trn['tour'] = response.meta['Trn'].tour
                plyr_trn['end_date'] = response.meta['Trn'].end_date
                plyr_trn['start_date'] = response.meta['Trn'].start_date
                plyr_trn['location'] = response.meta['Trn'].location

                yield plyr_trn

        yield

    def web_parse(self, response):
        # inspect_response(response,self)
        yield
