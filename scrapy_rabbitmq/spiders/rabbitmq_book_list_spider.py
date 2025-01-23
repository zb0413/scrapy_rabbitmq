# -*- coding: utf-8 -*-

from scrapy_rabbitmq.items import GenericItem
from scrapy_rabbitmq.spiders.rabbitmq_spider import RabbitmqSpider

class RabbitmqBookListSpider(RabbitmqSpider):
    name = "book-list-spider"

    custom_settings = {
        'ITEM_PIPELINES': {
            'bot_scrapy.pipelines.RabbitmqPipeline': 400,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'bot_scrapy.middlewares.RabbitmqMiddleware': 543,
        }
    }
    
    def parse(self, response):
        root_url = 'https://books.toscrape.com/'
        for book in response.css("article.product_pod"):
            url = root_url + book.css('h3 > a ::attr(href)').extract_first()
            title = book.css('h3 > a ::text').extract_first()
            file_urls = book.css('.image_container img ::attr(src)').extract()

            file_urls = [f'{root_url}{x}' for x in file_urls]

            item = GenericItem.create_new(response)
            item['url'] = url
            item['title'] = title
            item['file_urls'] = file_urls
            yield item

        
        # next_page = response.css("li.next > a ::attr(href)").extract_first()
        # if next_page:
        #     yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

        # next = response.css('.pager .next a::attr(href)').extract_first()
        # next_url = response.urljoin(next)
        # yield scrapy.Request(url=next_url, callback=self.parse)
    
