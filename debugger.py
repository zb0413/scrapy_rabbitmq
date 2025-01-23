from scrapy import cmdline

if __name__ == "__main__":
   cmdline.execute("scrapy runspider ./examples/rabbitmq_book_list_spider.py".split())