
import scrapy
from .ganji_urls import category, city
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging


class HLTItem(scrapy.Item):
    title = scrapy.Field()
    desc = scrapy.Field()

class GanjiSpider(CrawlSpider):
    name = 'ganji6'
    download_delay = 1

    allowed_domains = ['ganji.com'
    ]

    start_urls = [
        city + category[1],
        city + category[3],
        city + category[4],
        city + category[7],
        city + category[8],
        city + category[10],
        city + category[11],
        city + category[12],
        city + category[13],
        city + category[14],
        city + category[15],
    ]

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=[
                "//ul[@class='pageLink clearfix']",
                "//dl[@class='fenlei']"]),
            callback='parse'
        ),
        Rule(
            LinkExtractor(allow='/detail/\d+'),
            callback='parse_item'
        ),
        Rule(
            LinkExtractor(allow='/\d{8,}'),
            callback='parse_item_new'
        ),
    )

    def parse_item(self, response):
        try:
            item = HLTItem()
            name = response.xpath('normalize-space(//*[contains(concat( " ", @class, " " ), concat( " ", "info_titile", " " ))])').extract()
            add = response.xpath('normalize-space(//*[contains(concat( " ", @class, " " ), concat( " ", "baby_kuang", " " ))]//p)').extract()
            for k,v in zip(name,add):
                item['title'] = k
                item['desc'] = v
                return item
        except Exception as e:
            logging.exception("parse error")

    def parse_item_new(self, response):
        try:
            item = HLTItem()
            name = response.xpath('//title/text()').extract()
            add = response.xpath('/html/head/meta[@name="description"]/@content').extract()
            for k,v in zip(name,add):
                item['title'] = k
                item['desc'] = v
                return item
        except Exception as e:
            logging.exception("parse error")