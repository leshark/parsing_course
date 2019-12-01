from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from homework_5 import settings
from homework_5.spiders.hhru import HhruSpider
from homework_5.spiders.superjob import SuperjobSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SuperjobSpider)
    process.start()
