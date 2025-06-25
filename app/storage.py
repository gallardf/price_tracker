from datetime import datetime
from models import Price, Session, Product
from sqlalchemy.engine import URL

def save_price(data):
    session = Session()
    new_price = Price(
        date=datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S"),
        url=data["url"],
        title=data["title"],
        price=data["price"]
    )
    session.add(new_price)
    session.commit()
    session.close()

def get_all_prices():
    session = Session()
    prices = session.query(Price).order_by(Price.date.desc()).all()
    session.close()
    return prices

def clear_prices():
    session = Session()
    session.query(Price).delete()
    session.commit()
    session.close()

def add_product(url, title="", threshold=None):
    session = Session()
    new_product = Product(url=url, title=title, threshold=threshold)
    session.add(new_product)
    session.commit()
    session.close()

def get_all_products():
    session = Session()
    products = session.query(Product).order_by(Product.id).all()
    session.close()
    return products

def update_product(product_id, url=None, title=None, threshold=None):
    session = Session()
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
        if url is not None:
            product.url = url
        if title is not None:
            product.title = title
        if threshold is not None:
            product.threshold = threshold
        session.commit()
    session.close()

def delete_product(product_id):
    session = Session()
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
        session.delete(product)
        session.commit()
    session.close()
