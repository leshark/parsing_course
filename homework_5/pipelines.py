# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.jobsparser

    def process_item(self, item, spider):
        print(item)

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        return item

    def salaryHH(self):
        return 0
