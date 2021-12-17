import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader
import re

class CategorySpider(scrapy.Spider):
    name = 'leroymerlincategory'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/tovary-dlya-otdyha-na-dache/']

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.css('div[role="navigation"] a[data-qa-pagination-item="right"]::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        links = response.css(
            'div.largeCard a[data-qa="product-name"]::attr(href)'
        ).extract()
        for link in links:
            yield response.follow(link, callback=self.product_parse)

    def product_parse(self, response: HtmlResponse):
        name = response.css('h1.header-2::text').extract_first()
        price = response.css('meta[itemprop="price"]::attr(content)').extract_first()
        currency = response.css('meta[itemprop="priceCurrency"]::attr(content)').extract_first()
        articul = response.css('span[itemprop="sku"]::attr(content)').extract_first()
        brand = response.css('meta[itemprop="brand"]::attr(content)').extract_first()
        description = response.css(
            'section.pdp-section--product-description uc-pdp-section-vlimited.section__vlimit::text').extract_first()
        characteristics_names = response.css(
            'section.pdp-section--product-characteristicks uc-pdp-section-vlimited.section__vlimit dt.def-list__term::text').extract()
        characteristics_values = response.css(
            'section.pdp-section--product-characteristicks uc-pdp-section-vlimited.section__vlimit dd.def-list__definition::text').extract()
        characteristics = {}
        for i, value in enumerate(characteristics_names):
            result = re.search('^(\s+)?(.*?)(\s+)?$', characteristics_names[i])
            name = result.group(2)
            result = re.search('^(\s+)?(.*?)(\s+)?$', characteristics_values[i])
            value = result.group(2)
            characteristics[name] = value

        photos = response.css('uc-pdp-media-carousel picture source::attr(srcset)').extract()

        loader = ItemLoader(item=LeroymerlinItem())
        loader.add_value('url', response.url)
        loader.add_value('brand', brand)
        loader.add_value('name', name)
        loader.add_value('price', price)
        loader.add_value('currency', currency)
        loader.add_value('articul', articul)
        loader.add_value('description', description)
        loader.add_value('characteristics', characteristics)
        loader.add_value('photos', photos)
        yield loader.load_item()
