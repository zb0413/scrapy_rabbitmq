# Scrapy-RabbitMQ 分布式爬虫系统

这是一个基于Scrapy和RabbitMQ的分布式爬虫系统，使用Redis进行URL去重。

## 特性

- 使用RabbitMQ进行任务分发
- Redis实现URL去重
- 支持分布式部署
- 可扩展的爬虫框架

## 安装依赖

```bash
pip install -r requirements.txt
```

## 前置条件

- Python 3.7+
- RabbitMQ 服务器
- Redis 服务器

## 配置

1. RabbitMQ配置
   - 默认连接URL: `amqp://guest:guest@localhost:5672/`
   - 可在settings.py中修改 `RABBITMQ_CONNECTION_URL`

2. Redis配置
   - 默认连接URL: `redis://localhost:6379`
   - 可在settings.py中修改 `REDIS_URL`

## 使用方法

1. 创建新的爬虫
```python
from scrapy_rabbitmq.spiders import RabbitmqSpider

class YourSpider(RabbitmqSpider):
    name = 'your_spider'
    
    def start_requests(self):
        urls = [
            'http://example.com',
        ]
        for url in urls:
            self.push_request(url)
            
    def parse(self, response):
        # 实现你的解析逻辑
        pass
```

2. 运行爬虫
```bash
scrapy crawl your_spider
```

## 分布式部署

1. 确保所有节点都能访问相同的RabbitMQ和Redis服务器
2. 在每个节点上运行相同的爬虫
3. RabbitMQ会自动进行任务分发

## 监控

- 使用RabbitMQ管理界面（默认端口15672）监控队列状态
- 通过Scrapy的stats收集器查看爬虫状态

## 注意事项

- 确保RabbitMQ和Redis服务器正常运行
- 适当配置并发和下载延迟，避免对目标站点造成压力
- 在生产环境中建议配置代理和更复杂的请求头

## 贡献

欢迎提交问题和Pull Request！

## 许可证

MIT License

python -m scrapy_rabbitmq.spiders
python -m tests.push_url