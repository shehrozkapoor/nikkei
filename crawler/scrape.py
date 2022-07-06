from datetime import date, timedelta

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from jpx_crawler.spiders.futures import FuturesSpider



@click.command()
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today() - timedelta(days=1)))
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today() - timedelta(days=1)))
def scrape(date_start, date_end):
    process = CrawlerProcess(get_project_settings())
    process.crawl(FuturesSpider, date_start, date_end)
    process.start()


if __name__ == '__main__':
    scrape()
