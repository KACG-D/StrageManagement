
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from datetime import datetime

if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite3', echo=True)
    Base.metadata.create_all(engine)  # テーブル作成
 
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)

    def __init__(self, name=None):
        self.name = name
        
    def __repr__(self):
        return str((self.id,self.name))
 
class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer)
    total_amount = Column(Integer)
    date = Column(DateTime, default=datetime.now())

    def __init__(self,store_id=None,total_amount=None,date=None):
        self.store_id=store_id
        self.total_amount=total_amount
    def __repr__(self):
        return '<Title %r>' % (self.title)

class OrderedProduct(Base):
    __tablename__ = 'ordered_product'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    num = Column(Integer)

    def __init__(self,product_id=None,order_id=None,num=None):
        self.product_id = product_id
        self.product_id=product_id
        self.order_id=order_id
        self.num=num
    def __repr__(self):
        return str(self.order_id)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    purchase_price= Column(Integer)
    selling_price= Column(Integer)
    category_id= Column(Integer)
    stock= Column(Integer)
    store_id = Column(Integer)
    identifer = Column(String(128))
    def __init__(self, name=None,purchase_price=None,selling_price=None,category_id=None,stock=None,store_id=None,identifer=None):
        self.name = name
        self.purchase_price=purchase_price
        self.selling_price=selling_price
        self.category_id=category_id
        self.stock = stock
        self.store_id=store_id
        self.identifer=identifer

    def __repr__(self):
        return self.name

class Store(Base):
    __tablename__ = 'store'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    address = Column(String(128))
    phone = Column(String(128))
    mail = Column(String(128))
    advanced = Column(String(128))

    def __init__(self, name=None,phone=None,address=None,mail=None,advanced=""):
        self.name = name
        self.address=address
        self.phone=phone
        self.mail=mail
        self.advanced=advanced
        
    def __repr__(self):
        return self.name
