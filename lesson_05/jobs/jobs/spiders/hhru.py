import scrapy
from scrapy.http import HtmlResponse
from jobs.items import JobsItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://izhevsk.hh.ru/search/vacancy?area=&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.css('a.bloko-button[data-qa="pager-next"]::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacansy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)'
        ).extract()
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('div.vacancy-title h1.bloko-header-1::text').extract_first()
        salary = response.css('div.vacancy-title p.vacancy-salary span.bloko-header-2::text').extract()
        yield JobsItem(name=name, salary=salary)
