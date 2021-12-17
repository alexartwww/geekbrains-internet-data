import random
import re

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from jobs.items import JobsItem
import datetime


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.css('a.f-test-button-dalshe::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacansy = response.xpath('//div[contains(@class, "f-test-search-result-item")]//a[contains(@href, "vakansii")]/@href').extract()
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath('//div[contains(@class, "f-test-vacancy-base-info")]//h1/text()').extract_first()

        code = SuperjobSpider.name + '-' + str(random.randint(1000000000, 9999999999))
        match = re.search('-(\d+)\.html.*?$', response.url)
        if match:
            code = SuperjobSpider.name + '-' + str(match.group(1))

        compensation = ''.join(response.css('div.oVw62 span.ZON4b *::text').extract())
        compensation = compensation.replace('\xa0', '').replace('\u202f', '')

        minCompensation = ''
        maxCompensation = ''
        currency = ''
        tax = ''
        if compensation:
            matchFromTo = re.search('([\d\ ]+)—([\d\ ]+)([\S]+)', compensation)
            matchFrom = re.search('от ([\d\ ]+)([\S]+)', compensation)
            matchTo = re.search('до ([\d\ ]+)([\S]+)', compensation)
            if matchFromTo:
                minCompensation = str(matchFromTo.group(1)).replace(' ', '')
                maxCompensation = str(matchFromTo.group(2)).replace(' ', '')
                currency = str(matchFromTo.group(3)).replace(' ', '').replace('/месяц', '')
            elif matchFrom:
                minCompensation = str(matchFrom.group(1)).replace(' ', '')
                currency = str(matchFrom.group(2)).replace(' ', '').replace('/месяц', '')
            elif matchTo:
                maxCompensation = str(matchTo.group(1)).replace(' ', '')
                currency = str(matchTo.group(2)).replace(' ', '').replace('/месяц', '')

        # ====================================================

        location = response.css('p[data-qa="vacancy-view-location"]::text').extract_first()
        address = ''.join(
            response.css('div.vacancy-company-wrapper span[data-qa="vacancy-view-raw-address"] *::text').extract())
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
        loader.add_value('parser', SuperjobSpider.name)
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
