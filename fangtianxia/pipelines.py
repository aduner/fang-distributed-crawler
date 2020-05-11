# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from .items import NowHouseItem, EsfItem


class FangtianxiaPipeline:
    def __init__(self):
        # 连接本地mysql
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'debian-sys-maint',
            'password': 'lD3wteQ2BEPs5i2u',
            'database': 'fang',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self._sql_newhouse = None
        self._sql_esf = None

    @property
    def sql_newhouse(self):
        # 初始化sql语句
        if not self._sql_newhouse:
            self._sql_newhouse = '''
                  insert into newhouse(id,province,city,district,name,price,area,rooms,sale,origin_url)\
                  values(null,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        return self._sql_newhouse

    @property
    def sql_esf(self):
        # 初始化sql语句
        if not self._sql_esf:
            self._sql_esf = '''
                  insert into esf(id,province,city,address,price,unit_price,title,name,rooms,floor,area,years,toward,origin_url)\
                  values(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        return self._sql_esf

    def process_item(self, item, spider):
        if isinstance(item, NowHouseItem):
            # 提交新房数据
            defer_newhouse = self.dbpool.runInteraction(self.insert_newhouse_item, item)
            # 错误处理
            defer_newhouse.addErrback(self.handle_error, item, spider)
        else:
            # 提交二手房数据
            defer_esf = self.dbpool.runInteraction(self.insert_esf_item, item)
            defer_esf.addErrback(self.handle_error, item, spider)

    def insert_newhouse_item(self, cursor, item):
        # 执行SQL语句,存入新房子数据
        cursor.execute(self.sql_newhouse, (item['province'],
                                           item['city'],
                                           item['district'],
                                           item['name'],
                                           item['price'],
                                           item['area'],
                                           item['rooms'],
                                           item['sale'],
                                           item['origin_url'],))

    def insert_esf_item(self, cursor, item):
        # 执行SQL语句,存入二手房数据
        cursor.execute(self.sql_esf, (item['province'],
                                      item['city'],
                                      item['address'],
                                      item['price'],
                                      item['unit_price'],
                                      item['title'],
                                      item['name'],
                                      item['rooms'],
                                      item['floor'],
                                      item['area'],
                                      item['years'],
                                      item['toward'],
                                      item['origin_url'],))

    def handle_error(self, item, error, spider):
        print(error)
        print()
