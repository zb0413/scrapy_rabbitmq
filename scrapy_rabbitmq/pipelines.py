# -*- coding: utf-8 -*-
"""
Item pipelines for bot_scrapy
"""
import json
import logging
import pika
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)

class RabbitmqPipeline:

    def __init__(self, spider):
        self.spider = spider

    @classmethod
    def from_crawler(cls, crawler):
        return cls(spider=crawler.spider)


    def process_item(self, item, spider):
        self.spider.publish_msg(self.spider.items_queue_name , json.dumps(ItemAdapter(item).asdict()))
        return item

