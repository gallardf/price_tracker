from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DB_URL

Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    url = Column(String)
    title = Column(String)
    price = Column(Float)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String)
    threshold = Column(Float, nullable=True)

def init_db():
    Base.metadata.create_all(engine)

engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)