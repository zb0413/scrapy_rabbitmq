# -*- coding: utf-8 -*-
import logging
from scrapy import signals
from itemadapter import is_item, ItemAdapter
from importlib import import_module
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from urllib.parse import urlparse
import json
import uuid
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class RabbitmqMiddleware:

    def __init__(self, spider):
        self.spider = spider


    @classmethod
    def from_crawler(cls, crawler):
        return cls(spider=crawler.spider)


    def process_request(self, request, spider):
        logger.info("process_spider_input request %s", request)
        logger.info("request_scheduled spider %s", request)
        payload = {
            'meta': request.meta,
            'url': request.url,
            'update_at': datetime.now().isoformat(),
            'status': "pendding",
        }
        self.spider.publish_msg(self.spider.response_queue_name, json.dumps(payload))
        return None


    def process_exception(self, request, exception, spider):
        url = request.url
        payload = {
            'meta': request.meta,
            'url': request.url,
            'site': urlparse(url).netloc,
            'request_status': 'request_exception',
            'error_msg': str(exception),
            'result_encoding': request.encoding,
            'status': "error",
        }
        self.spider.publish_msg(self.spider.response_queue_name , json.dumps(payload))


    def process_response(self, request, response, spider):
        logger.info("request_received spider %s", response)
        url = request.url
        page_title = response.xpath('//title/text()').extract_first()
        page_title = page_title.strip() if page_title else ''
        
        payload = {
            'meta': request.meta,
            'url': request.url,
            'scrapy_date': datetime.now().isoformat(),
            'page_title': page_title,
            'site': urlparse(url).netloc,
            'request_status': 'response_received',
            'response_text': response.text,
            'result_encoding': request.encoding,
            'status': "finished",
        }
        self.spider.publish_msg(self.spider.response_queue_name, json.dumps(payload))
        return response