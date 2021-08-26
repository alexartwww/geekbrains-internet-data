# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class LeroymerlinPipeline:

    def open_spider(self, spider):
        self.client = MongoClient('mongodb://root:eeB5vu7aaiwie9Wo@127.0.0.1:27117')
        self.mongobase = self.client.geekbrains

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item


class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]

        return item
