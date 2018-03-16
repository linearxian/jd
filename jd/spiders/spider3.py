
import scrapy
from ganji_urls import category, city
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class HLTItem(scrapy.Item):
    title = scrapy.Field()
    desc = scrapy.Field()

class GanjiSpider(CrawlSpider):
    name = 'ganji3'
    download_delay = 1

    allowed_domains = ['ganji.com'
    ]

    start_urls = [
        city + category[5]
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

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(GanjiSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()