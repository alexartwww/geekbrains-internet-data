import random
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from jobs.items import JobsItem
import datetime


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.css('a.bloko-button[data-qa="pager-next"]::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacansy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)'
        ).extract()
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        url = response.url
        name = response.css('div.vacancy-title h1.bloko-header-1::text').extract_first()

        code = HhruSpider.name + '-' + str(random.randint(1000000000, 9999999999))

        match = re.search('hh\.ru/vacancy/(\d+).*?$', response.url)
        if match:
            code = HhruSpider.name + '-' + str(match.group(1))

        compensation = ''.join(response.css('div.vacancy-title p.vacancy-salary *::text').extract())
        compensation = compensation.replace('\xa0', '').replace('\u202f', '')

        minCompensation = ''
        maxCompensation = ''
        currency = ''
        tax = ''

        matchFromTo = re.search('от ([\d\ ]+) до ([\d\ ]+)([\S]+)\s+?(до вычета налогов|на руки)?', compensation)
        matchFrom = re.search('от ([\d\ ]+)([\S]+)\s+?(до вычета налогов|на руки)?', compensation)
        matchTo = re.search('до ([\d\ ]+)([\S]+)\s+?(до вычета налогов|на руки)?', compensation)

        if matchFromTo:
            minCompensation = str(matchFromTo.group(1)).replace(' ', '')
            maxCompensation = str(matchFromTo.group(2)).replace(' ', '')
            currency = str(matchFromTo.group(3)).replace(' ', '')
            tax = str(matchFromTo.group(4))
        elif matchFrom:
            minCompensation = str(matchFrom.group(1)).replace(' ', '')
            currency = str(matchFrom.group(2)).replace(' ', '')
            tax = str(matchFrom.group(3))
        elif matchTo:
            maxCompensation = str(matchTo.group(1)).replace(' ', '')
            currency = str(matchTo.group(2)).replace(' ', '')
            tax = str(matchTo.group(3))

        location = response.css('p[data-qa="vacancy-view-location"]::text').extract_first()
        address = ''.join(response.css('div.vacancy-company-wrapper span[data-qa="vacancy-view-raw-address"] *::text').extract())
        experience = response.css('span[data-qa="vacancy-experience"]::text').extract_first()

        if not address and location:
            address = location

        timetype = ''
        placetype = ''
        mode = response.css('p[data-qa="vacancy-view-employment-mode"]::text').extract_first()
        if mode:
            match = re.search('(.+), (.+)', mode)
            if match:
                timetype = str(match.group(1))
                placetype = str(match.group(2))

        company = ''.join(response.css('a[data-qa="vacancy-company-name"] *::text').extract())
        description = ''.join(response.css('div[data-qa="vacancy-description"] *::text').extract())
        keys = response.css('span[data-qa="bloko-tag__text"]::text').extract()

        dt = ''.join(response.css('p[class="vacancy-creation-time"] *::text').extract())

        loader = ItemLoader(item=JobsItem())
        loader.add_value('downloaded', datetime.datetime.now().isoformat())
        loader.add_value('updated', datetime.datetime.now().isoformat())
        loader.add_value('parser', HhruSpider.name)
        loader.add_value('code', code)
        loader.add_value('url', url)
        loader.add_value('datetime', dt)
        loader.add_value('name', name)
        loader.add_value('compensation', compensation)
        loader.add_value('min', minCompensation)
        loader.add_value('max', maxCompensation)
        loader.add_value('currency', currency)
        loader.add_value('tax', tax)
        loader.add_value('address', address)
        loader.add_value('experience', experience)
        loader.add_value('timetype', timetype)
        loader.add_value('placetype', placetype)
        loader.add_value('company', company)
        loader.add_value('description', description)
        loader.add_value('keys', keys)
        yield loader.load_item()
