# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv

from items import HupuUserItem, HupuItem
from scrapy.exporters import CsvItemExporter


class HupuPipeline(object):
    def __init__(self):
        self.f = open('hupu-user.csv', 'wb')
        self.hupu_f = open('hupu.csv', 'wb')
        # f = open('hupu-user.csv', 'wb')
        # self.writer = csv.writer(f)
        # self.writer.writerow(['user_id', 'gender', 'city', 'grade', 'online_time', 'join_time'])

    def open_spider(self, spider):
        self.hupu_user_to_export = {}
        self.hupu_to_export = {}

    def close_spider(self, spider):
        self.hupu_user_to_export.finish_exporting()
        self.hupu_to_export.finish_exporting()
        self.f.close()
        self.hupu_f.close()

    def _exporter_for_item(self, item):
        exporter = CsvItemExporter(self.f, include_headers_line=False)
        exporter.start_exporting()
        self.hupu_user_to_export = exporter
        return self.hupu_user_to_export

    def _exporter_for_hupu_item(self, item):
        exporter = CsvItemExporter(self.hupu_f, include_headers_line=False)
        exporter.start_exporting()
        self.hupu_to_export = exporter
        return self.hupu_to_export

    def process_item(self, item, spider):
        if isinstance(item, HupuUserItem):
            exporter = self._exporter_for_item(item)
            exporter.export_item(item)
            return item
        if isinstance(item, HupuItem):
            exporter = self._exporter_for_hupu_item(item)
            exporter.export_item(item)
            return item
