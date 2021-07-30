import re
from bs4 import BeautifulSoup
import requests
from hyper.contrib import HTTP20Adapter
import urllib
import requests
import json
from bs4 import BeautifulSoup as bs
import csv

task = '''
Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
с сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:

Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную и максимальную).
Ссылку на саму вакансию.

Сайт, откуда собрана вакансия. ### По желанию можно добавить ещё параметры вакансии
(например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas.
'''


def hhSearchParser(url, html):
    vacancies = []
    soup = bs(html, 'lxml')
    blocks = soup.find_all('div', {"class": "vacancy-serp-item"})

    for block in blocks:
        vacancy = {'name': '', 'link': '', 'compensation': None, 'min': None, 'max': None, 'currency': None}
        title = block.find('a', {"data-qa": "vacancy-serp__vacancy-title"})
        if title:
            vacancy['name'] = str(title.text)
            vacancy['link'] = urllib.parse.urljoin(url, str(title['href']))
        compensation = block.find('span', {"data-qa": "vacancy-serp__vacancy-compensation"})
        if compensation:
            vacancy['compensation'] = str(block.find('span', {"data-qa": "vacancy-serp__vacancy-compensation"}).text).replace('\u202f','')
            matchFromTo = re.search('([\d\ ]+)–([\d\ ]+)([\S]+)', vacancy['compensation'])
            matchFrom = re.search('от ([\d\ ]+)([\S]+)', vacancy['compensation'])
            matchTo = re.search('до ([\d\ ]+)([\S]+)', vacancy['compensation'])
            if matchFromTo:
                vacancy['min'] = str(matchFromTo.group(1)).replace(' ', '')
                vacancy['max'] = str(matchFromTo.group(2)).replace(' ', '')
                vacancy['currency'] = str(matchFromTo.group(3)).replace(' ', '')
            elif matchFrom:
                vacancy['min'] = str(matchFrom.group(1)).replace(' ', '')
                vacancy['currency'] = str(matchFrom.group(2)).replace(' ', '')
            elif matchTo:
                vacancy['max'] = str(matchTo.group(1)).replace(' ', '')
                vacancy['currency'] = str(matchTo.group(2)).replace(' ', '')
        vacancies.append(vacancy)
    return vacancies


def hhVacancyParser(url, html):
    pass


class Spider():
    def __init__(self):
        self.rules = {}
        self.urls = []
        self.headers = {}
        self.data = []
        self.downloadLimit = None

    def setDownloadLimit(self, downloadLimit):
        self.downloadLimit = downloadLimit

    def setHeaders(self, headers):
        self.headers = headers

    def addUrl(self, url, referer='', cookie=''):
        for link in self.urls:
            if link['url'] == url:
                return
        link = {
            'url': url,
            'referer': referer,
            'cookie': cookie,
            'downloaded': False,
            'status_code': None
        }
        self.urls.append(link)

    def addRule(self, rule, parser=None):
        self.rules[rule] = parser

    def log(self, message):
        print(message)

    def addUrlsByRules(self, url, html, referer='', cookie=''):
        soup = bs(html, 'lxml')
        links = soup.find_all('a', href=True)
        for link in links:
            for pattern in self.rules:
                fullLink = urllib.parse.urljoin(url, link['href'])
                if re.search(pattern, fullLink):
                    self.addUrl(fullLink, referer=referer, cookie=cookie)

    def parse(self, url, html):
        for pattern in self.rules:
            if re.search(pattern, url):
                parsed = self.rules[pattern](url, html)
                if parsed:
                    if type(parsed) == dict:
                        self.data.append(parsed)
                    elif type(parsed) == list:
                        self.data += parsed

    def loop(self):
        counter = 0
        while True:
            forCounter = 0
            for i, _ in enumerate(self.urls):
                if self.urls[i]['downloaded']:
                    continue
                headers = self.headers.copy()
                if self.urls[i]['referer']:
                    headers['referer'] = self.urls[i]['referer']
                if self.urls[i]['cookie']:
                    headers['cookie'] = self.urls[i]['cookie']
                response = requests.get(self.urls[i]['url'], headers=headers)
                forCounter += 1
                counter += 1
                self.urls[i]['downloaded'] = True
                self.urls[i]['status_code'] = response.status_code
                self.log(str(response.status_code) + ' ' + self.urls[i]['url'])
                if self.urls[i]['status_code'] == 200:
                    self.addUrlsByRules(self.urls[i]['url'], response.text, self.urls[i]['referer'],
                                        self.urls[i]['cookie'])
                    self.parse(self.urls[i]['url'], response.text)
                if self.downloadLimit and counter >= self.downloadLimit:
                    break
            if (forCounter == 0) or (self.downloadLimit and counter >= self.downloadLimit):
                break

    def dumpData(self, filename):
        if len(self.data) == 0:
            return
        keys = self.data[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.data)


if __name__ == '__main__':
    print(task)

    text = 'python'
    spider = Spider()
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
    spider.addUrl(
        url='https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=' + text,
        referer='https://hh.ru/',
        cookie='__ddg1=pSja5kZ5NyKtCiXcBWHQ; regions=1; region_clarified=NOT_SET; hhuid=bBl1XilWfI5pJWC4iBsgDg--; __ddgid=ZhE7Rd7SO9EYJJuX; _fbp=fb.1.1622706204310.838106499; _ym_uid=1608300436498838273; _ym_d=1622706204; tmr_lvid=2f6c61c248238933686e671b09307bf3; tmr_lvidTS=1617621208061; iap.uid=a67989bbcf7b479c8e089e63efb69f63; __gads=ID=4c631050ed331fe8:T=1622706207:S=ALNI_Ma_20rXdDCubl4tf-HYbtfEWHflFg; __ddg2=ciojkTsti6pDb7IO; hhtoken=aNVfdsEhxaJp6\u00213xTEzMDQytggXo; hhul=b0435a80dd4f0eade99750daf8909556d8a1fdd371220e713b9c835ce62b833b; hhul=b0435a80dd4f0eade99750daf8909556d8a1fdd371220e713b9c835ce62b833b; __zzatgib-w-hh=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS9HcXVaRCEfHEcTUnkOCjRaGRY1cCoNODxjc0NuMCw/ZR1kTl8ldVkLayELUTQ1ZhBKT01HDTdAXjdXYSAMFhFNVlN7KhkSe3EmUA4OWzkzPDRtc3hcJgoaVDVfGUNqTg1pN2wXPHVlL3kmPmEtOhlRCyBWfBt8OVZcSWl1bkFNPB8Kdl99G0FtJGVQWSg1UT9BWltUODZnQRFPJQp2aWVtdCpSUVFaJUVaTXopHxR4ciZSe3Uqdg0tDmh6KFYcOWNjDSIKdRddWj8oFVlxSx9uejM/XgsxDzQcFcd/yQ==; _xsrf=a3ccb92bfdda3e3d7b72cb78dd363901; _xsrf=a3ccb92bfdda3e3d7b72cb78dd363901; hhrole=anonymous; display=desktop; GMT=3; __ddgmark=NrrZ3vss49gO9K4e; _ga_44H5WGZ123=GS1.1.711b04eb40c91c1b1fcb446fd7175444397729ac2e71d83e440c67522dd59dd0.5.0.1627435126.60; _ga=GA1.2.1873493662.1622706204; _gid=GA1.2.472485952.1627435127; _ym_isad=2; _ym_visorc=w; _gat_gtag_UA_11659974_2=1; cfidsgib-w-hh=l6P4Z0zjT/VA9lplXvhdahIya1usK0fZTeIkliFecyb9UGI+W8gaBBEOSVPtXfyej7KuiP0Her/Y2s181YbXftRzTmn2mOo0AItM7CTypGaeKmNxBJUIEMqgQRelU43agw5N7Pg8as7VOBd7oRssH9uvK8XONp5s7bYs5vw=; cfidsgib-w-hh=l6P4Z0zjT/VA9lplXvhdahIya1usK0fZTeIkliFecyb9UGI+W8gaBBEOSVPtXfyej7KuiP0Her/Y2s181YbXftRzTmn2mOo0AItM7CTypGaeKmNxBJUIEMqgQRelU43agw5N7Pg8as7VOBd7oRssH9uvK8XONp5s7bYs5vw=; gsscgib-w-hh=W94TAg2SHRmIJZmpVKYU/H6NvIVoUCjdQ3lCYvusci8ysrHM4RGFzH+Wq3mUx0a1sfF+KYHuS+7ZyhMlH4/5TU4PMtY6lIwe4gcTk8vDfpdHng5pTuGGzeQeG9iyXVJcEi9+oaSPPIr36gT4q00P6qPIaktODSO41v8MvmQBc2u1xADptbTrT7yH8dtCrzh/TwVmuHMuLEwJset5iORnVpI9NI1ZY5bO3rQuUbvDwPG0/W5wMEBB4+i7LFF2iw==; tmr_detect=0%7C1627435130153; tmr_reqNum=44; fgsscgib-w-hh=uJ4j116351297be1c2a820682d4beab1a5ac82b5'
    )
    spider.addRule(
        '^https:\/\/hh\.ru\/search\/vacancy\?area=1&fromSearchLine=true&st=searchVacancy&text=.*?(&page=\d+)?',
        parser=hhSearchParser
    )
    # spider.addRule(
    #     '^https:\/\/hh\.ru\/vacancy\/\d+',
    #     parser=hhVacancyParser
    # )
    spider.setDownloadLimit(100)

    spider.loop()
    spider.dumpData('vacancies.csv')

    # url = 'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=python'
    # pattern = '^https:\/\/hh\.ru\/search\/vacancy\?area=1&fromSearchLine=true&st=searchVacancy&text=.*?(&page=\d+)?'
    # print(re.search(pattern, url))
