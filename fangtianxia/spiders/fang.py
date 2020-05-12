# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from ..items import NowHouseItem, EsfItem
import scrapy

class FangSpider(RedisSpider):
    name = 'fang'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:strat_urls"
    province = None

    def parse(self, response):
        '''
        爬取省份和城市，传递城市url进一步分析
        '''
        print("---")
        trs = response.xpath("//div[@class='outCont']//tr")
        for tr in trs:
            province = tr.xpath("./td/strong/text()").get()
            if province:
                if province == '其它':
                    break
                self.province = province
            cities = tr.xpath("./td[last()]//a")
            for c in cities:
                city = c.xpath("./text()").get()
                city_url = c.xpath("./@href").get()
                city_logogram = city_url.split("//")[1].split(".")[0]  # 从url中解析城市简称
                if city == '北京':
                    city_newhouse_url = f'http://newhouse.fang.com/house/s/'
                    city_esf_url = f'http://esf.fang.com'
                else:
                    city_newhouse_url = f'http://{city_logogram}.newhouse.fang.com/house/s/'
                    city_esf_url = f'http://{city_logogram}.esf.fang.com'
                yield scrapy.Request(url=city_newhouse_url, callback=self.parse_newhouse,
                                     meta={'info': (province, city)})
                yield scrapy.Request(url=city_esf_url, callback=self.parse_esf,
                                     meta={'info': (province, city)})

    def parse_newhouse(self, response):
        province, city = response.meta.get('info')
        lis = response.xpath("//div[@class='nl_con clearfix']/ul/li")
        for li in lis:
            district = li.xpath(".//div[@class='address']/a/@title").get()
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if name == None:
                # 这种是什么都没有的，不知道为还挂在上面，直接舍弃
                continue
            else:
                name = name.strip()
            price = li.xpath(".//div[@class='nhouse_price']//text()").getall()
            price = "".join(price).strip()
            area = ''.join(li.xpath(".//div[@class='house_type clearfix']/text()").getall())
            area = area.replace('/', '').replace('－', '').strip()
            if area == '':
                area = "暂无数据"
            rooms = li.xpath(".//div[@class='house_type clearfix']/a/text()").getall()
            rooms = '/'.join(rooms).strip()
            sale = li.xpath(".//span[@class='forSale' or @class='inSale' or @class='outSale']/text()").get()
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()[2:]
            item = NowHouseItem(
                province=province,
                city=city,
                district=district,
                name=name,
                price=price,
                area=area,
                rooms=rooms,
                sale=sale,
                origin_url=origin_url
            )
            yield item
        next_url = response.xpath("//div[@class='otherpage']/a[2]/@href").get()  # 获取下一页
        if next_url:
            next_url = response.urljoin(next_url)
            return scrapy.Request(url=next_url, callback=self.parse_newhouse,
                                  meta={'info': (province, city)})
        else:
            return

    def parse_esf(self, response):
        province, city = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            try:
                address = dl.xpath(".//p[@class='add_shop']/span/text()").get()
                price = ''.join(dl.xpath(".//span[@class='red']//text()").getall())
                unit_price = dl.xpath(".//dd/span[not(@class)]//text()").get()
                title = dl.xpath(".//span[@class='tit_shop']//text()").get()
                name = dl.xpath(".//h4[@class='clearfix']//span/text()").get()
                name = name.replace('\n', '').replace(" ", '')
                rooms = dl.xpath(".//p[@class='tel_shop']/text()[1]").get().strip()
                area = dl.xpath(".//p[@class='tel_shop']/text()[2]").get().strip()
                floor = dl.xpath(".//p[@class='tel_shop']/text()[3]").get().strip()
                toward = dl.xpath(".//p[@class='tel_shop']/text()[4]").get().strip()
                years = dl.xpath(".//p[@class='tel_shop']/text()[5]").get()
                if years:
                    years = years.strip()
                    if years == '':
                        years = "暂无数据"
                else:
                    years = "暂无数据"
                origin_url = response.urljoin(dl.xpath(".//h4[@class='clearfix']//a/@href").get())
            except AttributeError:
                # 出错原因是某个数据没有，绝大多数的房子最多没有年份
                # 这里出错的大多是那种信息很少的，直接抛弃
                continue
            item = EsfItem(
                province=province,
                city=city,
                address=address,
                price=price,
                unit_price=unit_price,
                title=title,
                name=name,
                rooms=rooms,
                floor=floor,
                area=area,
                years=years,
                toward=toward,
                origin_url=origin_url
            )
            yield item
        next_url = response.urljoin(response.xpath("//a[contains(text(), '下一页')]/@href").get())
        if next_url:
            return scrapy.Request(url=next_url, callback=self.parse_esf,
                                  meta={'info': (province, city)})
        else:
            return
