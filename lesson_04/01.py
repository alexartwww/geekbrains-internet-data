import re
from bs4 import BeautifulSoup
import requests
import urllib
import requests
import json
from bs4 import BeautifulSoup as bs
import csv
from pymongo import MongoClient
import random
import datetime
import lxml.html as lh

task = '''
Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru,
yandex-новости. Для парсинга использовать XPath.

Структура данных должна содержать:

- название источника;
- наименование новости;
- ссылку на новость;
- дата публикации.
'''

class Spider():
    def __init__(self):
        self.rules = {}
        self.urls = []
        self.headers = {}
        self.data = []
        self.downloadLimit = None
        self.parseLimit = None
        self.connectionString = 'mongodb://root:eeB5vu7aaiwie9Wo@127.0.0.1:27117'
        self.dbName = 'geekbrains'
        self.db = None
        self.client = None

    def setDataHandler(self, dataHandler):
        self.addDataHandler = dataHandler

    def setDownloadLimit(self, downloadLimit):
        self.downloadLimit = downloadLimit

    def setParseLimit(self, parseLimit):
        self.parseLimit = parseLimit

    def setHeaders(self, headers):
        self.headers = headers

    def addDocument(self, code, typedoc, url, referer='', cookie=''):
        for link in self.urls:
            if link['url'] == url:
                return
        document = {
            'code': code,
            'type': typedoc,
            'url': url,
            'referer': referer,
            'cookie': cookie,
            'added_at': datetime.datetime.utcnow(),
            'downloaded_at': None,
            'parsed_at': None,
            'status_code': None,
            'headers': {},
            'html': '',
            'data': {}
        }
        if self.db.documents.count_documents({'code': document['code']}) == 0:
            self.log('Insert document ' + document['code'])
            self.db.documents.insert(document)

    def updateDocument(self, code, **kwargs):
        if self.db.documents.count_documents({'code': code}) > 0:
            self.log('Update document ' + code)
            setDocument = {
                'downloaded_at': datetime.datetime.utcnow()
            }
            setDocument.update(kwargs)
            self.db.documents.update(
                {
                    'code': code
                },
                {
                    '$set': setDocument
                }, upsert=False, multi=False)

    def addRule(self, rule, typedoc=None, coder=None, parser=None):
        self.rules[rule] = {'parser': parser, 'coder': coder, 'type': typedoc}

    def addDocumentsByRules(self, url, html, referer='', cookie=''):
        soup = bs(html, 'lxml')
        links = soup.find_all('a', href=True)
        for link in links:
            for pattern in self.rules:
                fullLink = urllib.parse.urljoin(url, link['href'])
                if re.search(pattern, fullLink):
                    code = self.rules[pattern]['coder'](fullLink)
                    typedoc = self.rules[pattern]['type']
                    if code:
                        self.addDocument(code=code, typedoc=typedoc, url=fullLink, referer=referer, cookie=cookie)

    def log(self, *args):
        print(' '.join([str(a) for a in args]))

    def download(self):
        counter = 0
        while True:
            self.log('Getting 10 documents')
            forCounter = 0
            cursor = self.db.documents.find({'downloaded_at': None}, limit=10)
            for document in cursor:
                headers = self.headers.copy()
                if document['referer']:
                    headers['referer'] = document['referer']
                if document['cookie']:
                    headers['cookie'] = document['cookie']
                self.log('Requesting document', document['code'], document['url'])
                response = requests.get(document['url'], headers=headers)
                self.log('Status', response.status_code)
                data = {}
                self.log('Parsing document', document['code'], document['url'])
                for pattern in self.rules:
                    if re.search(pattern, document['url']) and self.rules[pattern]['parser']:
                        data = self.rules[pattern]['parser'](document['url'], response.text)
                self.log('Parsed', len(data), document['code'], document['url'])
                self.log('Adding links', document['code'], document['url'])
                self.addDocumentsByRules(document['url'], response.text, referer=document['referer'], cookie=headers['cookie'])
                self.log('Added', document['code'], document['url'])
                self.log('Updating document', document['code'], document['url'])
                self.updateDocument(document['code'],
                                    downloaded_at=datetime.datetime.utcnow(),
                                    parsed_at=datetime.datetime.utcnow(),
                                    headers=response.headers,
                                    status_code=response.status_code,
                                    html=response.text,
                                    data=data)
                self.log('Updated', len(data), document['code'], document['url'])
                counter += 1
                forCounter += 1
                if self.downloadLimit and counter > self.downloadLimit:
                    break
            if forCounter == 0 or self.downloadLimit and counter > self.downloadLimit:
                break

    def parse(self):
        counter = 0
        while True:
            self.log('Getting 10 documents')
            forCounter = 0
            cursor = self.db.documents.find({'parsed_at': {'$eq': None}, 'downloaded_at': {'$ne': None}}, limit=10)
            for document in cursor:
                data = {}
                self.log('Parsing document', document['code'], document['url'])
                for pattern in self.rules:
                    if re.search(pattern, document['url']) and self.rules[pattern]['parser']:
                        data = self.rules[pattern]['parser'](document['url'], document['html'])
                self.log('Parsed', len(data), document['code'], document['url'])
                self.log('Updating document', document['code'], document['url'])
                self.updateDocument(document['code'],
                                    parsed_at=datetime.datetime.utcnow(),
                                    data=data)
                self.log('Updated', len(data), document['code'], document['url'])
                counter += 1
                forCounter += 1
                if self.parseLimit and counter > self.parseLimit:
                    break
            if forCounter == 0 or self.parseLimit and counter > self.parseLimit:
                break

    def dbConnect(self):
        self.client = MongoClient(self.connectionString)
        self.db = self.client[self.dbName]

def yandexNewsStoryCoder(url):
    regex = '^https:\/\/yandex\.ru\/news\/story\/.*?--([0-9abcdef]+)'
    find = re.search(regex, url)
    if find:
        return 'yandex-news-story-' + str(find.group(1))
    return None

def yandexNewsStoryParser(url, html):
    data = {}
    try:
        root = lh.fromstring(html)
        data['title'] = root.xpath("//article[contains(@class, 'mg-story')]/h1[contains(@class, 'mg-story__title')]/a/text()")[0]
        data['text'] = ' '.join(root.xpath("//article[contains(@class, 'mg-story')]//div[contains(@class, 'mg-snippet')]//span[contains(@class, 'mg-snippet__text')]/text()"))
        data['datetime'] = datetime.datetime.strptime(root.xpath("//meta[@property='article:published_time']/@content")[0], "%Y-%m-%dT%H:%M:%S.000Z")
    except:
        pass
    return data

if __name__ == '__main__':
    print(task)

    text = 'python'
    spider = Spider()
    spider.dbConnect()
    # spider.db.documents.update(
    #     {},
    #     {
    #         '$set': {'parsed_at': None}
    #     }, upsert=False, multi=True)
    spider.setHeaders({
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"\'',

        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',

        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    spider.addRule(
        '^https:\/\/yandex\.ru\/news\/story\/.*?--([0-9abcdef])',
        typedoc='yandex-news-story',
        coder=yandexNewsStoryCoder,
        parser=yandexNewsStoryParser
    )
    spider.addDocument(
        typedoc='yandex-news-home',
        code='yandex-news-home-01',
        url='https://yandex.ru/news/',
        referer='https://yandex.ru/',
        cookie='news_lang=ru; nc=tips=1625079576376%3Bfavorites-button:1; yandexuid=6501888421606004561; yuidss=6501888421606004561; gdpr=0; _ym_uid=1606008965991217000; is_gdpr=0; is_gdpr_b=CMmFQhD0DSgC; my=YwA=; font_loaded=YSv1; amcuid=1705012431612558395; mda=0; ymex=1921364561.yrts.1606004561#1935517088.yrtsi.1620157088; L=QU9pUVlzUlYBcH5YdWdLWlNAY1pWAXtbC0UfAjgdIBwEFFg+Gjw+Iw==.1620206550.14592.368976.05667f2a804a901283c4de019817f94a; yandex_login=artem.alexashkin; yandex_gid=213; i=hjzxUmxDPm+i3LfPQw7JVJq1ut8ZrYtQ6ChQdNUaKrw15AOmi32kMPPqIdysJdVNAftAwGuox4otFfX/pA+H4rwfAls=; spravka=dD0xNjI1ODc0ODEwO2k9ODUuMjQ5LjQ2LjE0NTtEPTNFQTFGNEMxQjYxNTM4NDIwNjEwNzMwNDNEODE1Qjk2OUY2QTVCNjZCRDI2NDMzMzExMUQzNUMyREY5RTNGMTQ7dT0xNjI1ODc0ODEwNjg2MTc2NjM4O2g9NWE4NDFmZmQ4N2FhNzVkOTg3Y2EzMTNkOTUzODZjMjg=; _ym_isad=2; Session_id=3:1628265934.5.0.1606008988768:6i_5VQ:87.1|76520527.0.2|82139251.300955.2.2:300955|3:238815.379988.0WRokpMTFHr-_oRsQivWitJvVIk; sessionid2=3:1628265934.5.0.1606008988768:6i_5VQ:87.1|76520527.0.2|82139251.300955.2.2:300955|3:238815.379988.0WRokpMTFHr-_oRsQivWitJvVIk; _ym_d=1628297557; yabs-frequency=/5/1m000AkKr6000000/F_zoS9G0000mGY62OK5jXW0002n28-0BSt2K0000C490/; yp=1935566550.udn.cDrQkNGE0L7QvdGP#1644047386.szm.1:1366x768:1366x599#1921669943.multib.1#1654190855.ygu.1#1630975968.csc.1#1656962665.nt.computers; _yasc=5Sk/BZIhiqElYzfYOdyx+coKrWUu/wT3qFqOs8nash8nqFdm6NEW/EC/Fsmizw==; cycada=ccj11qc2g2WnlNVdRCxMhwnjO6bsEI/APQDmg2qsru8='
    )
    spider.setDownloadLimit(10)
    spider.setParseLimit(10)
    spider.parse()
