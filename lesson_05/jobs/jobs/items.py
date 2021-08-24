# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from pymongo import MongoClient


class JobparserPipeline(scrapy.Item):
    def __init__(self):
        scrapy.Item.__init__(self)
        client = MongoClient('127.0.0.1', 27117)
        self.mongobase = client.geekbrains

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        print(item['salary'])

        return item
