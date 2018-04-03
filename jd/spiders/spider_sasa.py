
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class EnZhItem(scrapy.Item):
    Brand_en = scrapy.Field()
    Title_en = scrapy.Field()
    Desc_en = scrapy.Field()
    Brand_zh = scrapy.Field()
    Title_zh = scrapy.Field()
    Desc_zh = scrapy.Field()

class SasaSpider(CrawlSpider):
    name = 'sasa'
    download_delay = 1

    allowed_domains = ['sasa.com'
    ]

    start_urls = [
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218010000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218020000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218030000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218040000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218050000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218060000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218070000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218080000',
        'http://web1.sasa.com/SasaWeb/sch/category/listByCategory.jspa?functionId=0&brandId=0&categoryId=218090000',
    ]

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=[
                "//div[@class='box_list']"],
            allow='viewProductDetail'),
            callback='parse_item'
        ),
        Rule(
            LinkExtractor(restrict_xpaths=[
                # "//a[@class='btn_next']/@href"]),
                "//div[@class='pages']"]),
            callback='parse'
        ),
    )

    def parse_item(self, response):
        try:
            brand_zh = response.xpath("normalize-space(//div[@class='title']/a/span[@itemprop='brand'])").extract_first()
            title_zh = response.xpath("normalize-space(//div[@class='title']/a/span[@itemprop='name'])").extract_first()
            desc_zh = response.xpath("normalize-space(//div[@id='chapter-2']/div[@class='content'])").extract_first()
            if desc_zh:
                url_en = response.url.replace('sch', 'eng')
                request = scrapy.Request(url_en, callback=self.parse_item_en, meta={'Brand': brand_zh, 'Title': title_zh, 'Desc': desc_zh})
                yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_item_en(self, response):
        item = EnZhItem()
        item['Brand_zh'] = response.meta['Brand']
        item['Title_zh'] = response.meta['Title']
        item['Desc_zh'] = response.meta['Desc']
        try:
            item['Brand_en'] = response.xpath("normalize-space(//div[@class='title']/a/span[@itemprop='brand'])").extract_first()
            item['Title_en'] = response.xpath("normalize-space(//div[@class='title']/a/span[@itemprop='name'])").extract_first()
            item['Desc_en'] = response.xpath("normalize-space(//div[@id='chapter-2']/div[@class='content'])").extract_first()
            yield item
        except Exception as e:
            logging.exception("parse error")

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(SasaSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()