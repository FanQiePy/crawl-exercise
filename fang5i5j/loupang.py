# -*- coding: utf-8 -*-
import urllib2
import re
import csv
import urlparse
import zlib
import time
import pickle
import sys
import threading
import random
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from pymongo import MongoClient
from threading import Thread
from bson.binary import Binary
from gzip import GzipFile
from StringIO import StringIO

from kuaidaili import KuaidailiProxy

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
AREA_DICT = {
    'gongshuqu': '拱墅区',
    'xiachengqu': '下城区',
    'shangchengqu': '上城区',
    'xihuqu': '西湖区',
    'binjiangqu': '滨江区',
    'yuhangqu': '余杭区',
    'xiaoshanqu': '萧山区',
    'jianggangqu': '江干区'
}

AREA = (
    'jiangganqu', 'binjiangqu', 'xihuqu', 'shangchengqu',
    'yuhangqu', 'gongshuqu', 'xiachengqu', 'xiaoshanqu'
)

CITY = ('hz', )

HOUSE_TYPE = ('zufang', 'ershoufang')


class MongoCache(object):
    """采用MongoDB数据库缓存下载的html页面
    """
    def __init__(self, expires_days=30):
        self.client = MongoClient("mongodb://crawl:mongo666@localhost:27017", authSource='fivehouse', connect=False)
        self.db = self.client.fivehouse
        self.db.webpages.create_index('timestamp', expireAfterSeconds=timedelta(expires_days).total_seconds())
        self.lock = threading.RLock()

    def __getitem__(self, url):
        record = self.db.webpages.find_one({'_id': url})
        if record:
            return pickle.loads(zlib.decompress(record['result']))
            # return record['html']
        else:
            raise KeyError(url + 'does not exist')

    def __setitem__(self, url, result):
        self.lock.acquire()
        record = {'result': Binary(zlib.compress(pickle.dumps(result))), 'timestamp': datetime.utcnow()}
        # record = {'html': html, 'timestamp': datetime.utcnow()}
        self.db.webpages.update({'_id': url}, {'$set': record}, upsert=True)
        self.lock.release()

    def clear(self):
        self.db.webpages.drop()


class Throttle(object):
    """Throttle downloading by sleeping between requests to same domain
    """

    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        """Delay if have accessed this domain recently
        """
        domain = urlparse.urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


class Download(object):
    def __init__(self, delay=1, download_retries=5, proxy_retries=5):
        self.throttle = Throttle(delay)
        self.cache = MongoCache()
        self.num_retries = download_retries
        self.proxy_retries = proxy_retries
        self.proxy = KuaidailiProxy('https://hz.5i5j.com').proxy
        self.use_proxy = False

    def __call__(self, url):
        html = None
        if self.cache:
            try:
                result = self.cache[url]
                html = result['html'].decode("utf-8", 'replace')
            except KeyError:
                pass
        if html is None:
            self.throttle.wait(url)
            result = self.download(url)
            html = result['html']
            if self.cache:
                self.cache[url] = result
        if html is not None:
            # tree = BeautifulSoup(html, 'lxml')
            # name = tree.head.contents[0].name
            if re.match(u'<html><script>', html):
                self.use_proxy = True
                if self.proxy_retries > 0:
                    self.proxy_retries -= 1
                    self.cache_update(url)
                    return self.__call__(url)
                else:
                    print 'the website{} still can not be access, dammit!'.format(url)
        return html

    def cache_update(self, url):
        self.throttle.wait(url)
        result = self.download(url)
        if self.cache:
            self.cache[url] = result

    def download(self, url, user_agent=USER_AGENT):
        print'downloading url {}'.format(url)
        headers = {
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh'
        }
        request = urllib2.Request(url, headers=headers)
        opener = urllib2.build_opener()
        html = None
        code = None
        if self.use_proxy:
            proxy_params = {'http': random.choice(self.proxy)}
            opener.add_handler(urllib2.ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
            info = response.info().get('Content-Encoding')
            if info == 'gzip':
                html = self._gzip(html)
            elif info == 'deflate':
                html = self._deflate(html)
        except urllib2.HTTPError as e:
            if hasattr(e, 'code'):
                code = e.code
                if self.num_retries > 0 and 500 < code < 600:
                    self.num_retries -= 1
                    return self.download(url, user_agent)
                else:
                    print'{} error: {}'.format(e.code, e.reason)
            else:
                print'{} error: {}'.format(e.code, e.reason)
        return {'html': html, 'code': code}

    @staticmethod
    def _gzip(data):
        buf = StringIO(data)
        f = GzipFile(fileobj=buf)
        return f.read()

    @staticmethod
    def _deflate(data):
        try:
            return zlib.decompress(data, wbits=-zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)


class HouseCrawl(object):
    def __init__(self):
        self.download = Download()

    def house_info(self, city, house_type, area, page):
        # start_time = datetime.now()
        result_info = []
        if area is None:
            url = 'https://{}.5i5j.com/{}/{}/'.format(city, house_type, page)
        else:
            url = 'https://{}.5i5j.com/{}/{}/n{}/'.format(city, house_type, area, page)
        html = self.download(url)
        if html is not None:
            tree = BeautifulSoup(html, 'lxml')
            try:
                houses = tree.find('div', class_='list-con-box').ul.find_all('li')
            except AttributeError:
                result_info.append([city, area, house_type, page])
                # print(tree.encode('utf-8'))
                # print html
                # global houses
                # tree = BeautifulSoup(html, 'html.parser')
                # houses = tree.find('div', class_='list-con-box').ul.find_all('li')
            else:
                for house in houses:
                    # 收集该页中的所有住房信息
                    data = house.get_text()
                    try:
                        layout = re.search(u'\d(?:\s*)室(?:\s*).+(?:\s*)厅|多(?:\s*)室(?:\s*).+(?:\s*)厅',
                                           data).group().encode('utf-8')
                    except AttributeError as e:
                        print('layout', url, house, e)
                        continue
                    try:
                        square = re.search(u'(\d{1,3}(\.\d{1,2})?)(?:\s*)平米', data).group(1).encode('utf-8')
                    except AttributeError as e:
                        print('square', url, house, e)
                        continue
                    try:
                        put_date = re.search(u'\d{4}-\d{2}-\d{2}|今天|昨天|前天', data).group().encode('utf-8')
                        if put_date == '今天':
                            put_date = date.today().strftime('%Y-%m-%d')
                        elif put_date == '昨天':
                            put_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                        elif put_date == '前天':
                            put_date = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
                    except AttributeError as e:
                        print('date', url, house, e)
                        continue
                    try:
                        price = house.find('p', class_='redC').strong.string.encode('utf-8')
                        address = house.find('i', class_='i_02').next_sibling.string.encode('utf-8')
                        link = house.find('i', class_='i_02').next_sibling['href'].encode('utf-8')
                        house_url = 'https://{}.5i5j.com{}'.format(city, link).encode('utf-8')
                    except IndexError as e:
                        print(url, house, e)
                        continue
                    result_info.append([city, area, house_type, layout, square, price, put_date, address, house_url])
        else:
            print'html {} download failed!'.format(url)
            sys.exit()
        return result_info

    def house_page_info(self, city, house_type, area):
        """获取每一个区域的住房信息的总页面数
        """
        url = 'https://{}.5i5j.com/{}/{}/'.format(city, house_type, area)
        html = self.download(url)
        pages = None
        if html:
            tree = BeautifulSoup(html, 'lxml')
            try:
                pages = tree.find('div', class_='pageBox').find('div', class_='pageSty rf').find_all('a')[
                    1].string.decode('utf-8')
                if not re.search(u'\d', pages):
                    all_num = tree.find('div', class_='pageBox').find('div', class_='pageSty rf').get_text()
                    page_text = re.search(u'\d{1,3}', all_num)
                    if page_text:
                        pages = max(page_text.groups())
            except AttributeError:
                print'cant find element a in page {}'.format(url)
        return pages

    def house_info_queue(self, city_tuple=CITY, house_type_tuple=HOUSE_TYPE, area_tuple=AREA):
        """生成所需遍历的url列表
        """
        queue = []
        for city in city_tuple:
            for house_type in house_type_tuple:
                for area in area_tuple:
                    time.sleep(20)
                    pages = self.house_page_info(city, house_type, area)
                    if pages:
                        for page in range(1, int(pages) + 1):
                            queue.append([city, house_type, area, page])
                    else:
                        print'{} {} {} does not has pages info!'.format(city, house_type, area)
        print'all house info queue have been joined!'
        return queue


def threading_crawl(filename='house.csv', max_threads=5, sleep_time=5):
    """多线程抓取住房信息
    """
    house = HouseCrawl()
    start_time = datetime.now()
    crawl_queue = house.house_info_queue()
    threads = []

    f = open(filename, 'wb')
    writer = csv.writer(f)
    writer.writerows(
        [['city', 'area', 'house_type', 'layout', 'square', 'price', 'date', 'address', 'house_url'], ])

    def crawl_process():
        try:
            info_args = crawl_queue.pop()
        except IndexError:
            print('it has been done!')
        else:
            each_info = house.house_info(info_args[0], info_args[1], info_args[2], info_args[3])
            writer.writerows(each_info)

    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            thread = Thread(target=crawl_process)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        time.sleep(sleep_time)
    print'all data have been collected, total used time is {}min'.format(
                (datetime.now()-start_time).total_seconds()//60)
    f.close()


if __name__ == '__main__':
    threading_crawl()
    # C = MongoCache()
    # C.clear()
    # house_crawl = HouseCrawl()
    # information = house_crawl.house_info('hz', 'ershoufang', 'xiaoshanqu', '78')
    # print'it is done'
