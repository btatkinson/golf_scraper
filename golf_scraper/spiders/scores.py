# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import numpy as np
import datetime

from scrapy_splash import SplashRequest
from scrapy.selector import Selector

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
        trns=trns[:1]

        for trn in trns:
            date = datetime.strptime(trn.end_date, '%b %d %Y')
            if date > datetime.datetime.today().date():
                continue
            if trn.tour == 'PGA':
                sr = SplashRequest(url=trn.link, args={'timeout': 90,'wait':1}, callback=self.pga_parse)
            elif trn.tour == 'Euro':
                sr = SplashRequest(url=trn.link, args={'timeout': 90,'wait':1}, callback=self.euro_parse)
            elif trn.tour == 'Web':
                sr = SplashRequest(url=trn.link, args={'timeout': 90,'wait':1}, callback=self.web_parse)
            yield sr

    def pga_parse(self, response):
        # inspect_response(response,self)
        yield
    def euro_parse(self, response):
        # inspect_response(response,self)
        yield
    def web_parse(self, response):
        # inspect_response(response,self)
        yield
