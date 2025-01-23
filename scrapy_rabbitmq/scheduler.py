# -*- coding: utf-8 -*-
import logging
import json
import pika
from scrapy.utils.request import request_from_dict
from scrapy.http import Request
from scrapy import BaseScheduler

logger = logging.getLogger(__name__)

class Scheduler(BaseScheduler):  
    
    def __init__(self, crawler):
        super().__init__(crawler)
        self.spider = None
        
        
    def open(self, spider):
        """打开调度器"""
        self.spider = spider
        return self

        
    def has_pending_requests(self):
        """检查是否有待处理的请求"""
        if not self.spider.rabbitmq_channel or self.spider.rabbitmq_channel.is_closed:
            return False
        try:
            # 使用queue_declare获取队列信息
            queue = self.spider.rabbitmq_channel.queue_declare(
                queue=self.spider.inbound_queue_name,
                passive=True
            )
            return queue.method.message_count > 0
        except Exception as e:
            logger.error(f"Error checking pending requests: {e}")
            return False
            
            
    def __len__(self):
        """获取队列中的消息数量"""
        try:     
            queue = self.spider.rabbitmq_channel.queue_declare(
                queue=self.spider.inbound_queue_name,
                durable=True,
                passive=True
            )
            return queue.method.message_count
        except Exception as e:
            logger.error(f"Error getting queue length: {e}")
            return 0
