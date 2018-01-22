# -*- coding: utf-8 -*-
import urllib2
import urlparse
import time
import random
from bs4 import BeautifulSoup

KAUIDAILIURL = 'https://www.kuaidaili.com/free/'


class KuaidailiProxy(object):

    def __init__(self, url):
        self.proxy = []
        self.proxy_pool = []
        self._make_proxy_pool()
        # while self.proxy:
        #     proxy = self.proxy.pop(random.choice(range(len(self.proxy))))
        #     if self._check_proxy(url, proxy):
        #         break
        if self.proxy:
            length = len(self.proxy)
            for i in range(length):
                if self._check_proxy(url, self.proxy[i]):
                    self.proxy_pool.append(self.proxy[i])
        pass

    def _get_proxy(self, url):
        html = None
        try:
            html = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            pass
        if html:
            tree = BeautifulSoup(html, 'lxml')
            table = tree.body.div.find('div', id='content').table.tbody.find_all('tr')
            for tr in table:
                try:
                    host = tr.find_all('td', attrs={'data-title': 'IP'})[0].string
                    port = tr.find_all('td', attrs={'data-title': 'PORT'})[0].string
                    self.proxy.append('{}:{}'.format(host, port))
                except IndexError:
                    pass

    def _make_proxy_pool(self, pages=5):
        for page in range(1, pages+1):
            url = KAUIDAILIURL + 'inha/{}/'.format(page)
            self._get_proxy(url)
            time.sleep(2)

    @staticmethod
    def _check_proxy(url, proxy):
        opener = urllib2.build_opener()
        proxy_prams = {'http': proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_prams))
        request = urllib2.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh'
        })
        try:
            response = opener.open(request)
            code = response.code
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print e
            code = 500
        if 200 <= code < 300:
            return True
        else:
            return False


if __name__ == '__main__':
    k = KuaidailiProxy('https://hz.5i5j.com')
    print 'yes'
