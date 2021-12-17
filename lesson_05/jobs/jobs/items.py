# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def remove_symbols(value):
    if type(value) is str:
        return value.replace('\xa0', ' ').replace('\u202f', ' ')
    else:
        return value


class JobsItem(scrapy.Item):
    _id = scrapy.Field()
    downloaded = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    updated = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    parser = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    code = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    datetime = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    compensation = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    min = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    max = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    currency = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    tax = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    address = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    experience = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    timetype = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    placetype = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    company = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols),
        output_processor=TakeFirst()
    )
    keys = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_symbols)
    )
