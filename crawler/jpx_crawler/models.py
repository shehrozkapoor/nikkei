from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date
)
from scrapy.utils.project import get_project_settings

Base = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))

def create_table(engine):
    Base.metadata.create_all(engine)

class Future(Base):
    __tablename__ = "futures"
    id = Column(Integer, primary_key=True)
    date = Column('date', Date)
    jpx_code = Column('jpx_code', Integer)
    company_id = Column('company_id', Integer)
    instrument = Column('description', String(100))
    name_jpn = Column('name_jpn', String(255))
    name_eng = Column('name_eng', String(255))
    left_val = Column('left_val', Integer)
    right_val = Column('right_val', Integer)
    label = Column("label", String(100))

    def __repr__(self):
        return f"{self.date} {self.name_eng} {self.left_val} {self.right_val}"
