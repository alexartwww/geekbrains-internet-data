# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from pymongo import MongoClient


class JobsPipeline(object):

    def open_spider(self, spider):
        self.client = MongoClient('mongodb://root:eeB5vu7aaiwie9Wo@127.0.0.1:27117')
        self.mongobase = self.client.geekbrains

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.mongobase['jobs']
        if collection.find({'code': item['code']}).count() > 0:
            to_update = {}
            keys_to_update = [
                'updated',
                'datetime',
                'name',
                'compensation',
                'min',
                'max',
                'currency',
                'tax',
                'address',
                'experience',
                'timetype',
                'placetype',
                'company',
                'description',
                'keys'
            ]
            for key in keys_to_update:
                if key in item:
                    to_update[key] = item[key]
            collection.update(
                {'code': item['code']},
                {'$set': to_update},
                upsert=False,
                multi=False)
        else:
            collection.insert(item)

        return item
