import csv

from datetime import timedelta, datetime
from io import StringIO

from scrapy import Spider, Request
from jpx_crawler.items import JpxCrawlerItem


class FuturesSpider(Spider):
    name = 'futures'
    allowed_domains = ['jpx.co.jp']
    start_urls = ['https://www.jpx.co.jp/markets/derivatives/participant-volume/index.html']
    whole_day_url = ('{}_volume_by_participant_whole_day.csv')
    whole_day_jnet_url = ('{}_volume_by_participant_whole_day_J-NET.csv')

    def __init__(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end

    def parse(self, response):
        if 'archives' not in response.url:
            for i in range(1, 12):
                url = f'https://www.jpx.co.jp/markets/derivatives/participant-volume/archives-{str(i).zfill(2)}.html'
                yield Request(url, self.parse)

        for i in range((self.date_end - self.date_start).days + 1):
            day = (self.date_start + timedelta(days=i)).strftime('%Y%m%d')

            whole_day_url = response.xpath(
                f'//a[contains(@href, "{self.whole_day_url.format(day)}")]/@href').extract_first()
            if whole_day_url:
                yield Request(response.urljoin(whole_day_url), self.parse_whole_day, meta={'label': 'whole_day'})

            whole_day_jnet_url = response.xpath(f'//a[contains(@href, "{self.whole_day_jnet_url.format(day)}")]/@href').extract_first()
            if whole_day_jnet_url:
                yield Request(response.urljoin(whole_day_jnet_url), self.parse_whole_day,
                              meta={'label': 'whole_day_jnet'})

    def parse_whole_day(self, response):
        f = StringIO(response.text)
        data = [row for row in csv.reader(f, quotechar='"', skipinitialspace=True)]
        day = datetime.strptime(data[1][3], "%Y%m%d").date()
        for row in data[3:]:
            if not row:
                continue
            elif row[0] == 'JPX Code':
                jpx_code = row[1]
                continue
            elif row[0] == 'Instrument':
                instrument = row[1]
                continue

            company_id, name_jpn, name_eng, left_val, _, _, _, right_val = row

            yield JpxCrawlerItem(
                date=day,
                jpx_code=jpx_code,
                company_id=company_id.replace('-', ''),
                instrument=instrument,
                name_jpn=name_jpn,
                name_eng=name_eng,
                left_val=left_val.replace('-', ''),
                right_val=right_val.replace('-', ''),
                label=response.meta['label']
            )
