# -*- coding: utf-8 -*-

"""
RabbitMQ-based distributed spider implementation
"""
import logging
import json
import time
import pika
from scrapy import Spider, signals
from scrapy.http import FormRequest
from scrapy.exceptions import DontCloseSpider
from scrapy import version_info as scrapy_version
from collections.abc import Iterable
from scrapy.utils.project import get_project_settings

import scrapy
from ..items import GenericItem

logger = logging.getLogger(__name__)


# 默认的RabbitMQ连接参数
DEFAULT_CONNECTION_PARAMETERS = {
    'host': 'localhost',
    'port': 5672,
    'virtual_host': '/',
    'credentials': {
        'username': 'root',
        'password': 'root'
    },
    'heartbeat': 0,
    'blocked_connection_timeout': 300
}


class RabbitmqSpider(Spider):
    """Base spider using RabbitMQ for distributed crawling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        # self.batch_size = None
        self.max_idle_time = None
        self.spider_idle_start_time = int(time.time())
        self.inbound_queue_name = None
        self.response_queue_name = None
        self.items_queue_name = None
        
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        # Get settings
        settings = crawler.settings

        cls.connect_rabbitmq(spider, settings)
       
        crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)        
        
        return spider
    

    @classmethod
    def connect_rabbitmq(cls, spider, settings):
        params = settings.get('RABBITMQ_CONNECTION_PARAMETERS', {})
    
        # 合并默认参数和用户设置
        connection_params = DEFAULT_CONNECTION_PARAMETERS.copy()
        connection_params.update(params)

        inbound_queue_name = settings.get('RABBITMQ_INBOUND_QUEUE_NAME', '%(spider)s:requests')
        response_queue_name = settings.get('RABBITMQ_RESPONSE_QUEUE_NAME', '%(spider)s:responses')
        items_queue_name = settings.get('RABBITMQ_ITEMS_QUEUE_NAME', '%(spider)s:items')

        # 创建认证凭据
        credentials = pika.PlainCredentials(
            username=connection_params['credentials']['username'],
            password=connection_params['credentials']['password']
        )
        
        try:
            # 创建连接参数
            parameters = pika.ConnectionParameters(
                host=connection_params['host'],
                port=connection_params['port'],
                virtual_host=connection_params['virtual_host'],
                credentials=credentials,
                heartbeat=connection_params['heartbeat'],
                blocked_connection_timeout=connection_params['blocked_connection_timeout']
            )
        
            # 建立连接
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
        
            spider.inbound_queue_name = inbound_queue_name % {'spider': spider.name}
            spider.response_queue_name = response_queue_name % {'spider': spider.name}
            spider.items_queue_name = items_queue_name % {'spider': spider.name} 

            channel.queue_declare(
                queue=spider.inbound_queue_name,
                durable=True,  # 持久化队列
                arguments={
                    'x-max-priority': 10
                }
            )

            channel.queue_declare(
                queue=spider.response_queue_name,
                durable=True,  # 持久化队列
                arguments={
                    'x-max-priority': 10
                }
            )

            channel.queue_declare(
                queue=spider.items_queue_name,
                durable=True,  # 持久化队列
                arguments={
                    'x-max-priority': 10
                }
            )
            
            # spider.batch_size = settings.get('RABBITMQ_BATCH_SIZE', 16)
            spider.max_idle_time = settings.get('RABBITMQ_MAX_IDLE_TIME', 0)

            spider.rabbitmq_connection = connection
            spider.rabbitmq_channel = channel


        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise

    
    def start_requests(self):
        """Returns a batch of start requests from redis."""
        return self.next_requests()
        

    def next_requests(self):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            RabbitmqSpider.connect_rabbitmq(self, self.crawler.settings)

        """获取下一批请求"""
        found = 0
        try:
            method_frame, header_frame, body = self.rabbitmq_channel.basic_get(
                queue=self.inbound_queue_name,
                auto_ack=False
            )
            if method_frame:
                try:
                    request_data = json.loads(body.decode('utf-8'))
                    reqs = self.make_request_from_data(request_data)
                    if isinstance(reqs, Iterable):
                        for req in reqs:
                            yield req
                            found += 1
                    elif reqs:
                        yield reqs
                        found += 1
                    # 确认消息已处理
                    self.rabbitmq_channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                except Exception as e:
                    # 处理失败，重新入队
                    self.rabbitmq_channel.basic_nack(
                        delivery_tag=method_frame.delivery_tag,
                        requeue=True
                    )
                    logger.error(f"Error processing request: {e}")
        except Exception as e:
            logger.error(f"Error fetching request: {e}")
            
        if found:
            logger.debug(f"Read {found} requests from queue")
            
    
    def make_request_from_data(self, data):
        """Returns a `Request` instance for data coming from Redis.

        Overriding this function to support the `json` requested `data` that contains
        `url` ,`meta` and other optional parameters. `meta` is a nested json which contains sub-data.

        Along with:
        After accessing the data, sending the FormRequest with `url`, `meta` and addition `formdata`, `method`

        For example:

        .. code:: json

            {
                "url": "https://example.com",
                "callback": "parse",
                "meta": {
                    "job-id":"123xsd",
                    "start-date":"dd/mm/yy",
                },
                "cookies":{},
                "method":"POST",
            }

        If `url` is empty, return `[]`. So you should verify the `url` in the data.
        If `callback` is empty, the request object will set callback to 'parse', optional.
        If `method` is empty, the request object will set method to 'GET', optional.
        If `meta` is empty, the request object will set `meta` to an empty dictionary, optional.

        This json supported data can be accessed from 'scrapy.spider' through response.
        'request.url', 'request.meta', 'request.cookies', 'request.method'

        Parameters
        ----------
        data : bytes
            Message from redis.

        """
        if not isinstance(data, dict):
            logger.warning(
                "WARNING: String request is deprecated, please use JSON data format."
            )
            return FormRequest(url=data, dont_filter=True)
            
        url = data.get('url')
        if not url:
            logger.warning("Received request without URL")
            return None
            
        callback = getattr(self, data.get('callback', 'parse'))
        method = data.get('method', 'GET')
        meta = data.get('meta', {})
        headers = data.get('headers', {})
        cookies = data.get('cookies', {})
        dont_filter = data.get('dont_filter', True)
        
        return FormRequest(
            url=url,
            callback=callback,
            method=method,
            headers=headers,
            cookies=cookies,
            meta=meta,
            dont_filter=dont_filter
        )

        
    def spider_idle(self):
        """爬虫空闲时的处理"""
        if self.max_idle_time and int(time.time()) - self.spider_idle_start_time >= self.max_idle_time:
            return
            
        for req in self.next_requests():
            if scrapy_version >= (2, 6):
                self.crawler.engine.crawl(req)
            else:
                self.crawler.engine.crawl(req, spider=self)
            
        raise DontCloseSpider
        

    def spider_closed(self, spider):
        """爬虫关闭时的清理工作"""
        if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
            self.rabbitmq_connection.close()

    
    def publish_msg(self, routing_key, payload):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            RabbitmqSpider.connect_rabbitmq(self, self.crawler.settings)

        self.rabbitmq_channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=payload.encode('utf-8')
        )

