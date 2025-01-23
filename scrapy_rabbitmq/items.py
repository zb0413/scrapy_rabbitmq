# -*- coding: utf-8 -*-
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime
import json
from urllib.parse import urlparse
import uuid


class GenericItem(scrapy.Item):
    id = scrapy.Field()
    task_url_id = scrapy.Field()
    task_id = scrapy.Field()
    spider_name = scrapy.Field()

    url = scrapy.Field()
    page_title = scrapy.Field()
    # scrapy_date = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    category = scrapy.Field()
    site = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    file_urls = scrapy.Field()
    file_paths = scrapy.Field()
    item_status = scrapy.Field()
    extra_data = scrapy.Field()
    error_msg = scrapy.Field()

    def to_json(self):
        d = self.__dict__['_values']
        # d.update({
        #     'scrapy_date': self['scrapy_date'].isoformat(),
        # })
        return json.dumps(d)
    
    @staticmethod
    def create_new(response):
        item = GenericItem()
        item['id'] = str(uuid.uuid4())
        item['task_url_id'] = response.request.meta.get('id', '')
        # item['site'] = urlparse(item['url']).netloc
        return item


