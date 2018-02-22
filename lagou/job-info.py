# -*- coding: utf-8 -*-

import urllib
import requests
import json
import csv
import time
import random
import datetime
import threading

URL = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false&isSchoolJob=0'

ABSTRACT_KEYS = [
    'companyId', 'companyShortName', 'createTime', 'positionId', 'salary',
    'workYear', 'education', 'positionName', 'companySize'
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
REFERER = 'https://www.lagou.com/jobs/list_{}?city={}&cl=false&fromSearch=true&labelWords=&suginput='


class Download(object):

    def __init__(self, kd='', city='', user_agent=USER_AGENT, referer=REFERER):
        self.kd = kd
        self.city = urllib.quote(city)
        self.url = URL.format(city)
        self.headers = {
            'User-Agent': user_agent,
            'Referer': referer.format(kd, urllib.quote(city))
        }

    def get_job_count(self):
        response = requests.post(self.url, data={'pn': 1, 'first': 'true', 'kd': self.kd}, headers=self.headers)
        content = json.loads(response.content, encoding='utf-8')
        job_info = content['content']['positionResult']
        total_count = job_info['totalCount']
        result_size = job_info['resultSize']
        pages = (total_count // result_size) + 2
        return pages

    def get_job_info(self, filename='job-info.csv'):
        f = csv.writer(open(filename, 'wb'))
        rows = [ABSTRACT_KEYS, ]
        pages = self.get_job_count()
        for pageNo in range(1, pages):
            if pageNo == 1:
                first = 'true'
            else:
                first = 'false'
            try:
                print('ready to abstract jobs of page {}: {}'.format(pageNo, datetime.datetime.now()))
                time.sleep(random.randrange(10, 20))
                response = requests.post(self.url, data={'pn': pageNo, 'first': first, 'kd': self.kd}, headers=self.headers)
                content = json.loads(response.content, encoding='utf-8')
                try:
                    job_info = content['content']['positionResult']
                except KeyError:
                    print(content.msg.encode('utf-8'))
                    break
                for item in job_info['result']:
                    each_job_info = []
                    for info_key in ABSTRACT_KEYS:
                        value = item[info_key]
                        if type(value) is int:
                            each_job_info.append(value)
                        else:
                            each_job_info.append(value.encode('utf-8'))
                    rows.append(each_job_info)
            except requests.HTTPError as e:
                print(e)
        f.writerows(rows)
        print('it is done!')


def get_job_info_threads(city, keyword, page):
    rows = []
    if page == 1:
        first = 'true'
    else:
        first = 'false'
    try:
        print('ready to abstract jobs of page {}: {}'.format(page, datetime.datetime.now()))
        time.sleep(random.randrange(10, 20))
        response = requests.post(URL.format(city), data={'pn': page, 'first': first, 'kd': keyword},
                                 headers={
                                             'User-Agent': USER_AGENT,
                                             'Referer': REFERER.format(keyword, urllib.quote(city))
                                         })
        content = json.loads(response.content, encoding='utf-8')
        try:
            job_info = content['content']['positionResult']
        except KeyError:
            print(content['msg'].encode('utf-8'))
            time.sleep(120)
            get_job_info_threads(city, keyword, page)
        else:
            for item in job_info['result']:
                each_job_info = []
                for info_key in ABSTRACT_KEYS:
                    value = item[info_key]
                    if type(value) is int:
                        each_job_info.append(value)
                    else:
                        each_job_info.append(value.encode('utf-8'))
                rows.append(each_job_info)
    except requests.HTTPError as e:
        print(e)
    return rows


class ThreadsGetJobInfo(object):

    def __init__(self, cities=('杭州', ), keywords=('python', ), min_sleep_time=10, max_sleep_time=20):
        self.cities = cities
        self.keywords = keywords
        self.min_sleep_time = min_sleep_time
        self.max_sleep_time = max_sleep_time
        self.rows = [ABSTRACT_KEYS, ]
        self.crawl_queue = []
        self._get_job_first_page()

    def _get_job_first_page(self):
        for city in self.cities:
            for keyword in self.keywords:
                time.sleep(random.randint(self.min_sleep_time, self.max_sleep_time))
                pages = Download(keyword, city).get_job_count()
                for page in range(1, pages):
                    self.crawl_queue.append([city, keyword, page])

    def _get_job_process(self):
            try:
                page = self.crawl_queue.pop()
            except IndexError:
                print'All crawl has been dong!'
            else:
                page_rows = get_job_info_threads(page[0], page[1], page[2])
                self.rows.append(page_rows)

    def threads_get_job(self, max_threads=5):
        threads = []
        while threads or self.crawl_queue:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
            while len(threads) < max_threads and self.crawl_queue:
                thread = threading.Thread(target=self._get_job_process)
                thread.setDaemon(True)
                thread.start()
                threads.append(thread)
            time.sleep(random.randint(self.min_sleep_time, self.max_sleep_time))

    def save(self, filename):
        f = open(filename, 'wb')
        writer = csv.writer(f)
        writer.writerows(self.rows)


if __name__ == '__main__':
    job_info = ThreadsGetJobInfo(('杭州', '上海'), ('python', 'php'))
    job_info.threads_get_job()
    job_info.save('job-info-more.csv')

    # Download('python', '杭州').get_job_info()

