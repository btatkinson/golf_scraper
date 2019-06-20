# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import numpy as np
import datetime
import time
import math

from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
from scrapy.selector import Selector
from tabula import read_pdf

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

    skip_df = []


    def __init__(self, *args, **kwargs):
        super(ScoresSpider, self).__init__(*args, **kwargs)

    def get_tid(self, name, tour, season):
        name = name.strip()
        name = name.replace(" ","")
        season = str(season)
        return str(name+tour+season)

    def check_to_filter(self, trn, collected, skipped):
        should_filter = False

        tid = self.get_tid(trn.name, trn.tour, trn.season)

        # check if already collected
        if tid in collected:
            should_filter = True
        if tid in skipped:
            should_filter = True

        # check for other problems

        #check for no link
        if not isinstance(trn.link, str) and math.isnan(trn.link):
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "No Link"])

        if 'MatchPlay' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])

        if 'RyderCup' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Ryder Cup"])
        if 'RYDERCUP' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Ryder Cup"])

        if 'PresidentsCup' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Presidents Cup"])

        if 'Tigervs.Phil' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Tigervs.Phil"])

        if 'WorldCupofGolf' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "WorldCupofGolf"])

        if 'FranklinTempletonShootout' in trn.name:
            if int(trn.season) ==2000:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Doubles"])
        if 'VivendiSeveTrophy' in trn.name:
            if int(trn.season) ==2011:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'VivendiTrophywithSeveBallesteros' in trn.name:
            if int(trn.season) ==2009:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'RoyalTrophy' in trn.name:
            if int(trn.season) ==2009:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'ZurichClassicofNewOrleans' in trn.name:
            if int(trn.season) in [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Team Play"])
        if 'CompaqClassicofNewOrleans' in trn.name:
            if int(trn.season) in [2000,2001,2002]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Team Play"])
        if 'HPClassicofNewOrleans' in trn.name:
            if int(trn.season) in [2003,2004]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Team Play"])
        if 'EURASIACUPpresentedbyDRB-HICOM' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'Super6Perth' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'EuropeanGolfTeamChampionships' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'GolfSixes' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Match Play"])
        if 'SeveTrophy' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "MatchPlay"])
        if 'SeveTrophy*' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'WGC-TheWorldCup*' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'EurobetSeveBallesterosTrophy*' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        # missing
        if 'WGC-CadillacChampionship' in trn.name:
            if int(trn.season) in [2012]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])
        if 'OmegaMissionHillsWorldCup' in trn.name:
            if int(trn.season) in [2007,2008]:
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])
                should_filter = True
        if 'FijiInternational' in trn.name:
            if int(trn.season) in [2017]:
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])
                should_filter = True
        if 'Olympic' in trn.name:
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])
            should_filter = True
        if 'WGC-BarbadosWorldCup' in trn.name:
            if int(trn.season) in [2006]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])
        if 'QualifyingSchoolStage1-Moliets' in trn.name:
            if int(trn.season) in [2000]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])
        if 'EuropeanTourQualifyingSchoolFinals' in trn.name:
            if int(trn.season) in [2000]:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Missing"])

        # was cancelled
        if 'Cancelled' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'CANCELLED' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])

        if '*' in trn.name:
            if trn.tour =='Euro':
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'OMEGAMissionHillsWorldCup' in trn.name:
            if str(trn.year) =='2011':
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'WGC-EMCWorldCup*' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'AlfredDunhillCup*' in trn.name:
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'VikingClassic' in trn.name:
            if str(trn.year) =='2009':
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'TampaBayClassicpresentedbyBuick' in trn.name:
            if int(trn.season) ==2001:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])
        if 'WorldGolfChampionships-AmericanExpressChampionship' in trn.name:
            if int(trn.season) ==2001:
                should_filter = True
                self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Cancelled"])

        if trn.tour == 'Web':
            should_filter = True
            self.skip_df.append([tid, trn.name, trn.tour, trn.season, "Web"])

        return should_filter

    def fix_ty_pga(self, link):
        return link.replace('.html', '/past-results.html')

    def start_requests(self):

        # start scraping number
        START = 0
        END = 2500

        # load tournaments
        sched = pd.read_csv('./sched.csv')

        # load already collected
        collected = pd.read_csv('./has_saved.csv')
        collected = list(collected.TID.unique())

        # load already skipped
        old_skipped = pd.read_csv('./skipped.csv')
        skipped = list(old_skipped.TID.unique())

        # tournament object list
        trns = []
        for index, row in sched.iterrows():
            trn = Tournament(row)
            trns.append(trn)

        trns=trns[START:END]

        # testing
        # test_trns = []
        # for trn in trns:
        #     if trn.link == 'https://www.europeantour.com//europeantour/season=2015/tournamentid=2015008/leaderboard/index.html':
        #         test_trns.append(trn)
        # print('TEST TRN LINKS: ', len(test_trns))

        # count tournaments of the future
        ho_counter = 0
        for trn in trns:
            try:
                date = datetime.datetime.strptime(trn.end_date, '%b %d %Y').date()
            except:
                if trn.end_date == 'end_date':
                    continue
            if date > datetime.datetime.today().date():
                print("Hasn't occured")
                ho_counter += 1
                continue

            # check if it matches criteria to throw out
            should_filter = self.check_to_filter(trn, collected, skipped)

            if should_filter:
                continue

            # fix this year's pga
            if int(trn.season) == datetime.date.today().year:
                if trn.tour == 'PGA':
                    if "THEPLAYERS" in trn.name:
                        trn.link = 'https://www.theplayers.com/past-results.html'
                    else:
                        trn.link = self.fix_ty_pga(trn.link)

            print("TRNY: ", trn.name, trn.season)
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

        self.skip_df = pd.DataFrame(self.skip_df, columns=['TID', 'Tournament', 'Tour', 'Season', 'Reason'])
        new_skip_df = pd.concat([old_skipped,self.skip_df], sort=False)
        new_skip_df.drop_duplicates(subset ="TID",keep='first', inplace=True)
        new_skip_df.to_csv('./skipped.csv', index=False)

        print("NUMBER OF TOURNAMENTS ALREADY COLLECTED: ", len(collected))
        print("NUMBER OF TOURNAMENTS SKIPPED: ", len(new_skip_df))
        print("NUMBER OF TOURNAMENTS THAT HAVEN'T OCCURED: ", ho_counter)


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

        # for newer alternate tables
        if not table_found:
            table = response.xpath('//table[@id="lbl"]/tbody//tr')
        if len(table) > 0:
            table_found = True
            for row in table:
                plyr_trn = Player_Tournament()
                name = row.css('td.nm')
                if len(name) < 1:
                    continue
                name_text = name.css('div::text').getall()[0]
                plyr_trn['name'] = name_text
                pos = row.css('td.b::text').getall()[0]
                plyr_trn['pos'] = pos
                rnds = row.css('td.rnd::text').getall()
                rnd_num = 1
                while len(rnds) > 0:
                    rnd_name = 'R' + str(rnd_num)
                    plyr_trn[rnd_name] = rnds.pop(0)
                    rnd_num += 1

                plyr_trn['tournament'] = response.meta['Trn'].name
                plyr_trn['season'] = response.meta['Trn'].season
                plyr_trn['tour'] = response.meta['Trn'].tour
                plyr_trn['end_date'] = response.meta['Trn'].end_date
                plyr_trn['start_date'] = response.meta['Trn'].start_date
                plyr_trn['location'] = response.meta['Trn'].location

                yield plyr_trn

        # last resort, try pdf
        table_length = len(table)
        if table_length < 2:
            table_found = False
        if not table_found:
            print('TRYING PDF')
            try:
                tid = self.get_tid(response.meta['Trn'].name, response.meta['Trn'].tour, response.meta['Trn'].season)
                path = './pdfs/' + tid + '.pdf'
                print(path)
                df = read_pdf(path, pages='all')
                for index, row in df.iterrows():
                    plyr_trn = Player_Tournament()
                    plyr_trn['name'] = row['Name']
                    plyr_trn['pos'] = row['Pos']
                    plyr_trn['R1'] = row['1']
                    plyr_trn['R2'] = row['2']
                    plyr_trn['R3'] = row['3']
                    plyr_trn['R4'] = row['4']

                    plyr_trn['tournament'] = response.meta['Trn'].name
                    plyr_trn['season'] = response.meta['Trn'].season
                    plyr_trn['tour'] = response.meta['Trn'].tour
                    plyr_trn['end_date'] = response.meta['Trn'].end_date
                    plyr_trn['start_date'] = response.meta['Trn'].start_date
                    plyr_trn['location'] = response.meta['Trn'].location

                    yield plyr_trn
            except:
                pass

        yield

    def alt_euro_parse(self, response):
        inspect_response(response, self)


        return

    def web_parse(self, response):
        # inspect_response(response,self)
        yield
