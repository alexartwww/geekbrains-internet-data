from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from avito.spiders.images import ImagesSpider
from avito import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(ImagesSpider, mark='GIGABYTE')
    process.start()
