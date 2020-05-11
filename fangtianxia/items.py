# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NowHouseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 省份
    province = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 区域地址
    district = scrapy.Field()
    # 小区名字
    name = scrapy.Field()
    # 房价
    price = scrapy.Field()
    # 面积
    area = scrapy.Field()
    # 几居室
    rooms = scrapy.Field()
    # 在售情况
    sale = scrapy.Field()
    # 详情页面url
    origin_url = scrapy.Field()


class EsfItem(scrapy.Item):
    # 省份
    province = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 总价
    price = scrapy.Field()
    # 每平单价
    unit_price = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 小区名字
    name = scrapy.Field()
    # 格局（几室几厅）
    rooms = scrapy.Field()
    # 层高
    floor = scrapy.Field()
    # 面积
    area = scrapy.Field()
    # 年代
    years = scrapy.Field()
    # 朝向
    toward = scrapy.Field()
    #详情url
    origin_url=scrapy.Field()
