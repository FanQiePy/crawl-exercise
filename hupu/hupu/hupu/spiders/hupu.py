# -*- coding: utf-8 -*-
import requests
import re
import scrapy
from scrapy.spider import SitemapSpider
from ..items import HupuItem, HupuUserItem

URL = 'https://bbs.hupu.com/sitemap_index.xml'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
headers = {
    'User-Agent': USER_AGENT,
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml, image/jpeg',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh'
}


def _get_last_month_url():
    sitemap = []
    try:
        xml = requests.get(URL, headers=headers).text
        # 选择储存最近一个月的帖子的xml地址
        sitemap = re.findall('<loc>(.*?)</loc>', xml)[-30:]
    except requests.HTTPError:
        pass
    return sitemap


class HupuSpider(SitemapSpider):
    name = 'hupu'
    allowed_domains = ['hupu.com']

    sitemap_urls = _get_last_month_url()

    def parse_user(self, response):
        """用户信息解析"""
        item = HupuUserItem()
        try:
            item['user_id'] = re.search('\d+', response.url).group()
        except AttributeError:
            item['user_id'] = re.search('hupu\.com/(.*)', response.url).group(1)
        info = response.css('div.personalinfo')
        item['gender'] = ''
        item['city'] = ''
        try:
            item['gender'] = info.xpath(".//span[@itemprop='gender']/text()")[0].extract()
            item['city'] = info.xpath(".//span[@itemprop='address']/text()")[0].extract()
        except IndexError:
            pass
        try:
            item['grade'] = info.re(u'社区等级：</span>(\d+)')[0]
            item['online_time'] = info.re(u'在线时间：</span>(\d+)')[0]
            item['join_time'] = info.re(u'加入时间：</span>([0-9]+-[0-9]+-[0-9]+)')[0]
        except IndexError:
            pass
        yield item

    def parse(self, response):
        """最近一个月发表的主题解析"""
        item = HupuItem()
        # item['block'] = response.css('div.breadCrumbs a::text')[-1:].extract()
        # 主题所在板块
        item['block'] = response.css('div.breadCrumbs')[0].xpath('.//a[last()]/text()')[0].extract()
        # 主题标题
        title_div = response.css('div.bbs-hd-h1')
        item['title'] = title_div.xpath('.//h1/text()')[0].extract()
        # 主题回复数量
        item['reply_num'] = title_div.xpath('.//span/span[1]/text()')[0].re(r'(\d+)')
        # 主题发表日期
        item['date'] = response.css('div.floor_box').xpath(".//div[@class='left']")[0].xpath(
            ".//span[@class='stime']/text()")[0].extract()
        yield item

        # 楼主及回帖用户链接
        user_urls = response.css('a.u::attr(href)').extract()
        # 回帖页面的下一页链接
        next_page = response.css('div.hp-wrap div div#container div#t_main div.page div').xpath(
            ".//a[@class=nextPage]/@href").extract()
        # 生成用户信息页面请求
        for url in user_urls:
            yield scrapy.Request(url, callback=self.parse_user)

        # 如果有下一页则继续生成用户信息页面请求
        if next_page:
            yield scrapy.Request(next_page[0], callback=self.parse_user)
