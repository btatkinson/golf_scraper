# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SchedulePipeline(object):
    def process_item(self, item, spider):

        # handle date
        date = item['start_date']
        stripped = [x.strip() for x in date]
        date = " ".join(stripped)
        item['start_date'] = date

        info = item['location']
        if info:
            text = [x.strip() for x in info]
            text = [x.replace("\n","") for x in text]
            text = [x.replace(" ","") for x in text]
            text = [x.replace("\xa0"," ") for x in text]
            text = [x for x in text if len(x) > 0]
            info = " ".join(text)
            info = info.strip()
            item['location'] = info

        return item
