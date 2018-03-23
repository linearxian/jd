# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
import re
import requests
import time

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


def parse_answer(q_id):
    i = 1
    answers = []
    q_id = int(q_id)
    while True:
        with requests.session() as MySession:
            url = 'http://question.jd.com/question/getAnswerListById.action'
            data = {
                'questionId':'%d' %q_id,
                'page':i
            }
            data = MySession.get(url, params=data).text
            if data:
                lines = re.findall('"content":"(.*?)"', data)
                if lines:
                    print('--------------Parsing Answer Page %d--------------' %i)
                    print(lines)
                    answers.append(lines)
                else:
                    print('--------------Parse Question Finished--------------')
                    return answers
            else:
                print('--------------Parse Question Error--------------')
                break
            i = i + 1
            time.sleep(5)

def parse_product(p_id):
    i = 1
    content = []
    p_id = int(p_id)
    while True:
        with requests.session() as MySession:
            url = 'http://question.jd.com/question/getQuestionAnswerList.action'
            API = {
                'productId':'%d' %p_id,
                'page':i
            }
            data = MySession.get(url, params=API).text
            if data:
                lines = re.findall(r'"id":(\d+),"content":"(.*?)"', data)
                loop = 1
                if lines:
                    for QID,Question in lines:
                        print('--------------Parsing Question %d--------------' %loop)
                        print(Question)
                        answers = parse_answer(QID)
                        content.append(Question)
                        content.append(answers)
                        loop = loop + 1
                    print('--------------Parsing Product Finished--------------')
                    return content
            else:
                print('--------------Parsing Product Error--------------')
                break
            i = i + 1
            time.sleep(5)

class QAItem(scrapy.Item):
    content = scrapy.Field()

class JDConversationSpider(CrawlSpider):
    name = "JDConversation"
    download_delay = 3
    start_urls = [
        "http://list.jd.com/list.html?cat=9987,653,655&page=1&delivery=1&sort=sort_rank_asc&trans=1&JL=4_10_0#J_main"
    ]

    def parse(self,response):
        if response.status==200:
            try:
                all_goods = response.xpath("//div[@id='plist']/ul/li/div")
                for goods in all_goods:
                    item = QAItem()
                    pid = goods.xpath("@data-sku").extract()
                    if pid:
                        data_list = parse_product(pid[0])
                        for data in data_list:
                            item['content'] = data
                            yield item
            except Exception:
                print('--------------ERROR--------------')

            # find next page
            time.sleep(20)
            next_page = response.xpath('//a[@class="pn-next"]/@href').extract()
            if next_page:
                next_page = "https://list.jd.com" + next_page[0]
                print('--------------Finding next page--------------')
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                print('--------------There is no more page!--------------')

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(JDConversationSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()