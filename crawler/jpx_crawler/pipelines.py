# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from jpx_crawler.models import Future, db_connect, create_table


class JpxCrawlerPipeline(object):
    
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
    
    def process_item(self, item, spider):
        """Save discounts in the database
        This method is called for every item pipeline component
        """

        adapter = ItemAdapter(item)

        if adapter.get('company_id'):
            session = self.Session()
            future = Future(**item)

            try:
                session.add(future)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

            return item
        else:
            raise DropItem(f"Missing company_id in {item}")
