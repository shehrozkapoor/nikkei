# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


def serialize_index(value):
    return int(value) if value.isdigit() else None

class JpxCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    jpx_code = scrapy.Field(serializer=int)
    company_id = scrapy.Field(serializer=serialize_index)
    instrument = scrapy.Field(serializer=str)
    name_jpn = scrapy.Field(erializer=str)
    name_eng = scrapy.Field(erializer=str)
    left_val = scrapy.Field(serializer=serialize_index)
    right_val = scrapy.Field(serializer=serialize_index)
    label = scrapy.Field(serializer=str)
