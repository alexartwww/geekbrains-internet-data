import re
from bs4 import BeautifulSoup
import requests
from hyper.contrib import HTTP20Adapter

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

import requests
import json
from bs4 import BeautifulSoup as bs

if __name__ == '__main__':
    print(task)

    text = 'python'

    allow = [
        '^https:\/\/hh\.ru\/search\/vacancy\?area=1&fromSearchLine=true&st=searchVacancy&text=.*?&page=\d+'
        # '^https:\/\/hh\.ru\/vacancy\/\d+'
    ]

    urls = []
    url = {
        'referer': 'https://hh.ru/',
        'url': 'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=' + text,
        'downloaded': False,
        'http': 0
    }
    urls.append(url)

    # re.search(pattern, value)
    params = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': '__ddg1=qPZn3WEs6OuNJUxnn17w; regions=1; region_clarified=NOT_SET; hhuid=ZU8wCQ0w6bJiTWDwnYAhiw--; __ddgid=StWKs0lWMikF5OyJ; _fbp=fb.1.1626381697406.905423618; iap.uid=e260e820dd714aad800c7e7030003d0c; tmr_lvid=394e1a00889f6f2ab04036d50fe7fab2; tmr_lvidTS=1626381697431; __gads=ID=9ce427aab20583be:T=1626381697:S=ALNI_MbeQadYgRy-oQcqnFlyIq_MqVbzgg; __zzatgib-w-hh=MDA0dC0pXB4IH04NIH5rL2R7RSRfHDx1ZS9HcXVaRCEfHEcTUnkOCjRaGRY1cCoNODxjc0NuMCw/ZR1kTl8ldVkLayELUTQ1ZhBKT01HDTdAXjdXYSAMFhFNVlIJKx4XfmwqVggTYjkzPDRtc3hcJgoaVDVfGUNqTg1pN2wXPHVlL3kmPmEtOhlRCyBWfBt8OVZcSWl1bkFNPB8Kdl99G0FtJGVQWSg1UT9BWltUODZnQRFPJQp2aWVtdCpSUVFaJEtbUn8sGhh+bCtXe3Uqdg0tDmh6KFYcOWNjDSIKdRddWj8oFVlxSx9uejM/XgsxDzQcsUkP5g==; _ym_uid=1566129415989473158; _ym_d=1627065243; __ddgmark=2opfYxi66my9z3S4; _ym_isad=2; _gid=GA1.2.85950768.1627384111; _xsrf=39afc56ad99e0aada79ef98d15d518c0; _xsrf=39afc56ad99e0aada79ef98d15d518c0; hhrole=anonymous; display=desktop; hhtoken=7ngmti\u0021GL2yPRZJGhwLbbA0kbYPe; GMT=3; _ym_visorc=w; _ga_44H5WGZ123=GS1.1.bef3d9ced0f6f2a02a1d3a4c1844d3f9099fb7bec8b8e3cf360bb52559d70d65.5.1.1627431693.60; _ga=GA1.1.596841619.1626381698; _gat_gtag_UA_11659974_2=1; gssc58=; cfidsgib-w-hh=DCigPpIm6y1HCAsW6pEf2qavcSFzBZgJTSuj2XnyMmd7r5xEiok7WYVEisJ+/0cJRVncQoxUTgIjEzecu4L2oFVtwU7hS6pAi6dsRM2aT4hqHZyMFxwKnjscAL9ciH94OZvAc735fhkcv6fO8LuCVLsDJH+wc4bq5aCQ2g==; cfidsgib-w-hh=DCigPpIm6y1HCAsW6pEf2qavcSFzBZgJTSuj2XnyMmd7r5xEiok7WYVEisJ+/0cJRVncQoxUTgIjEzecu4L2oFVtwU7hS6pAi6dsRM2aT4hqHZyMFxwKnjscAL9ciH94OZvAc735fhkcv6fO8LuCVLsDJH+wc4bq5aCQ2g==; gsscgib-w-hh=8Ukr5WhMe1mGIH69f4iMh+2bpk6tBBasqotoi1LdogxqI402nGebuehP66rWwtqWqk73X0RBARVDIKRqutaw6dD9DUxMbJpF8q12SAn1giKTY/mLqELCN1zf3rqp9HAFaK7rB4xIadW5x4sPDPbaU8s/yBwfMSoFTgNSR0yO0yE40Kn1xetWEAzIw6mMyHe1eH0ZFXBHUdOJi1mwLahgpSiOXjNEM2dMeM1laN8Xr2kZeU8hs6V9VdiKetYZYg==; cto_bundle=QwHQ3V9OcHQlMkYlMkZ6VkRkJTJCdGk1ejJRNGF2eklhQVpkUXBiWU50M1FuTjR5NGpaZU9MbjV0WFE5UjB1JTJGVkhJTHBtcE9yYmMlMkJYaUljeXE4JTJGU3pBcFA2aUowTk1FWDNzUlZCU25qNjZkT3NqS2ZSV08zZEpvVVAxQmY4ZnU5d0doTEZRUmYlMkJDYnAlMkIxY3JHZnglMkY5eDBNJTJGdkFwY0diUSUzRCUzRA; tmr_detect=0%7C1627431697290; tmr_reqNum=45; fgsscgib-w-hh=zl4wb756c0ac848acb85d3bd9b027b931bc0e990'
        }
    }

    s = requests.Session()
    s.mount('https://hh.ru', HTTP20Adapter())

    for i, url in enumerate(urls):
        params['headers']['Referer'] = url['referer']
        response = s.get(url['url'], params=params)
        print(url['url'], response.status_code)
        urls[i]['downloaded'] = True
        urls[i]['http'] = response.status_code
        if urls[i]['http'] == 200:
            soup = bs(response.text, 'lxml')
            links = soup.find_all('a')
            for link in links:
                print(link.href)
