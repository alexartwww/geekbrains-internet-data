# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda value: float(value)),
        output_processor=TakeFirst(),
    )
    currency = scrapy.Field()
    articul = scrapy.Field()
    photos = scrapy.Field()
    characteristics = scrapy.Field()
