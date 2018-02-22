# -*- coding: utf-8 -*-
import scrapy
import urllib
import json
import re


POS_URL = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false&isSchoolJob=0'

Referer_URL = 'https://www.lagou.com/jobs/list_{}?city={}&cl=false&fromSearch=true&labelWords=&suginput='

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

CITIES = ['杭州', '上海', '北京', '深圳', '广州', '南京', '武汉', '成都', '天津', '重庆']

LANGUAGES = ['python', 'java', 'php', 'c++']


class ExampleSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    # start_urls = [POS_URL.format(urllib.quote('杭州'))]

    def start_requests(self):
        return [scrapy.FormRequest(POS_URL.format(urllib.quote(city)),
                                   formdata={'pn': '1', 'first': 'true', 'kd': keyword},
                                   headers={
                                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                                       'Accept-Encoding': 'gzip, deflate, br',
                                       'Accept-Language': 'zh-CN,zh;q=0.9',
                                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                       'User-Agent': USER_AGENT,
                                       'Referer': Referer_URL.format('python', urllib.quote(city)),
                                   },
                                   callback=self.parse) for city in CITIES for keyword in LANGUAGES]

    def parse(self, response):
        content = json.loads(response.text, encoding='utf-8')['content']
        position_result = content['positionResult']
        page_no = content['pageNo']
        page_size = content['pageSize']
        result = position_result['result']
        total_count = position_result['totalCount']
        # result_size = position_result['resultSize']

        pages = (total_count // page_size) + 1
        for item in result:
            yield item
        if page_no < pages:
            try:
                q = re.search('kd=([a-zA-Z]+)', response.request.body).group(1)
            except AttributeError:
                pass
            else:
                yield scrapy.FormRequest(response.url,
                                         formdata={'pn': str(page_no+1), 'first': 'false',
                                                   'kd': q},
                                         headers=response.request.headers,
                                         callback=self.parse)
