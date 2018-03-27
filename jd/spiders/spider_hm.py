
import scrapy
from scrapy.spiders import CrawlSpider
import logging
from lxml import html
import requests
import re
import time

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


def getPID(offset):
    with requests.session() as MySession:
        url = 'http://www2.hm.com/zh_cn/ladies/shop-by-product/view-all/_jcr_content/main/productlisting_30ab.display.html'
        API = {
            'product-type':'ladies_all',
            'sort':'stock',
            'offset':offset*30,
            'page-size':30

        }
        try:
            response = MySession.get(url, params = API)
            root = html.fromstring(response.content)
            PID = root.xpath("//article[@data-articlecode]/@data-articlecode")
            if PID:
                return PID
            else:
                return None
        except Exception as e:
            logging.exception("error")

class EnZhItem(scrapy.Item):
    PID = scrapy.Field()
    Title_en = scrapy.Field()
    Desc_en = scrapy.Field()
    Title_zh = scrapy.Field()
    Desc_zh = scrapy.Field()

class HMSpider(CrawlSpider):
    name = 'HandM'
    download_delay = 3

    allowed_domains = ['hm.com'
    ]

    def start_requests(self):
        # urls = [
        #     'http://www2.hm.com/zh_cn/productpage.0505071002.html',
        # ]
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse)
        i = 1
        while True:
            PIDs = getPID(i)
            if PIDs:
                for PID in PIDs:
                    url = 'http://www2.hm.com/zh_cn/productpage.' + PID + '.html'
                    yield scrapy.Request(url=url, callback=self.parse)
            else:
                break
            i = i + 1
            time.sleep(20)

    def parse(self, response):
        try:
            name = response.xpath("normalize-space(//h1[@class='primary product-item-headline'])").extract_first()
            add = response.xpath("normalize-space(//p[@class='pdp-description-text'])").extract_first()
            PID = re.findall('productpage.(\d+)', response.url)
            url_en = response.url.replace('zh_cn', 'en_cn')
            request = scrapy.Request(url_en, callback=self.parse_en, meta={'PID': PID, 'Title': name, 'Desc': add})
            yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_en(self, response):
        item = EnZhItem()
        item['PID'] = response.meta['PID']
        item['Title_zh'] = response.meta['Title']
        item['Desc_zh'] = response.meta['Desc']
        try:
            name = response.xpath("normalize-space(//h1[@class='primary product-item-headline'])").extract_first()
            add = response.xpath("normalize-space(//p[@class='pdp-description-text'])").extract_first()
            item['Title_en'] = name
            item['Desc_en'] = add
            yield item
        except Exception as e:
            logging.exception("parse error")


def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(HMSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()