# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import CsvItemExporter

class ScoresPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    # path = './leaderboard/'+self.season+'/'+self.tour+'/'+self.trn+'.csv'

    file = open('%s.csv' % spider.name, 'w+b')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file)
    self.exporter.fields_to_export = ["name", "pos", "R1", "R2", "R3", "R4", "tournament", "tour", "season", "location","start_date","end_date"]
    self.exporter.start_exporting()

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()

  def process_item(self, item, spider):
    item['name'] = item['name'].replace('"', '')
    self.exporter.export_item(item)
    return item



class SchedulePipeline(object):

    def clean_pga(self,item):
        date = item['start_date']
        stripped = [x.strip() for x in date]
        date = " ".join(stripped)
        item['start_date'] = date

        info = item['location']
        if info:
            info = [x.strip() for x in info]
            info = [x.replace("\n","") for x in info]
            info = [x.replace("\r","") for x in info]
            info = [x.replace("  ","") for x in info]
            info = [x.replace("\xa0"," ") for x in info]
            info = [x for x in info if len(x) > 0]
            info = " ".join(info)
            info = info.strip()

            purse_index = info.find("•")
            if purse_index > 0:
                info = info[:(purse_index-1)]
            item['location'] = info

        if item['link'] is not None:
            if ".com" not in item['link']:
                item['link'] = 'https://www.pgatour.com'+item['link']

        # fix date
        # see if it spans two calendar months
        d = item['start_date']
        month = ''.join(filter(str.isalpha, d))
        if len(month) > 3:
            split_d = d.split()
            item['start_date'] = " ".join(split_d[:2])
            item['end_date'] = " ".join(split_d[2:])
        else:
            split_index = d.replace('-',"")
            l_d = split_index.split()
            item['start_date'] = month + " " + l_d[1]
            item['end_date'] = month + " " + l_d[2]
        return item

    def clean_euro(self, item):

        if item['link'] is not None:
            if ".com" not in item['link']:
                item['link'] = 'https://www.europeantour.com/'+item['link']
                item['link'] = item['link'].replace('/index.html','/leaderboard/index.html')

        return item

    def clean_web(self, item):
        info = item['location']
        if info:
            info = info.replace("\n","")
            info = info.replace("\r","")
            info = info.replace(" ","")
            info = info.replace("\xa0"," ")
            purse_index = info.find("•")
            if purse_index > 0:
                info = info[:(purse_index-1)]
            item['location'] = info

        if item['link'] is not None:
            if ".com" not in item['link']:
                item['link'] = 'https://www.pgatour.com/webcom'+item['link']

        d = item['start_date']
        month = ''.join(filter(str.isalpha, d))
        if len(month) > 3:
            split_d = d.split()
            item['start_date'] = " ".join(split_d[:2])
            item['end_date'] = " ".join(split_d[2:])
        else:
            split_index = d.replace('-',"")
            l_d = split_index.split()
            item['start_date'] = month + " " + l_d[1]
            item['end_date'] = month + " " + l_d[2]

        return item

    def process_item(self, item, spider):

        raise ValueError('Using schedule pipeline')
        if spider == 'schedules':
            if item['tour'] == 'PGA':
                item = self.clean_pga(item)

            if item['tour'] == 'Euro':
                item = self.clean_euro(item)

            if item['tour'] == 'Web':
                item = self.clean_web(item)

            item['start_date'] = item['start_date'] + " " + str(item['year'])
            item['end_date'] = item['end_date'] + " " + str(item['year'])

        return item
