import scrapy
from scrapy.http import HtmlResponse
from avito.items import AvitoItem
from scrapy.loader import ItemLoader

class ImagesSpider(scrapy.Spider):
    name = 'avitoimages'
    allowed_domains = ['avito.ru']
    start_urls = ['http://avito.ru/']

    def __init__(self, mark):
        super().__init__()
        self.start_urls = [f'https://www.avito.ru/rossiya/bytovaya_elektronika?q={mark}']

    def parse(self, response: HtmlResponse, **kwargs):
        ads_links = response.xpath('//div[contains(@class, "iva-item-root")]//a[contains(@class, "iva-item-title")]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        name = response.css('h1.title-info-title span.title-info-title-text::text').extract().first()
        photos = response.xpath('//div[@class="gallery-img-frame"]/img/@src').extract()
        price = 0

        yield AvitoItem(name=name, photos=photos, price=price)
        print(name, photos, price)
