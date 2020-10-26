import os
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, \
  Table, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate

database_name = "myfridge"
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()
migrate = Migrate()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all()


"""
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database

    Keyword arguments: n/a
    argument -- n/a
    Return: return_description
"""
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


'''
User-Product association table
'''
user_products = Table('user_products', db.Model.metadata,    
      Column('user_id', Integer, ForeignKey('users.id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True),
      Column('product_id', Integer, ForeignKey('products.id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True))

'''
User
'''
class User(db.Model):  
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True)
  first_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)
  age = Column(Integer)
  products = db.relationship('Product', secondary='user_products',
                            backref=db.backref('users', lazy=True))
  current_products = Column(String)
  past_products = Column(String)
  date_registered = Column(DateTime)

  def __init__(self, first_name, last_name, age):
    self.first_name = first_name
    self.last_name = last_name
    self.age = age
    self.current_products={}
    self.past_products={}


  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'first_name': self.first_name,
      'last_name': self.last_name,
      'current_products': self.current_products,
      'past_products': self.past_products,
      'date_registered': self.date_registered
    }

  def __repr__(self):
        return f'<User {self.id}: {self.last_name}, {self.first_name}>'


'''
Product

'''
class Product(db.Model):  
  __tablename__ = 'products'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  weight = Column(String)
  quantity = Column(String)
  date_purchased = Column(Integer)
  image_link = Column(String)

  def __init__(self, name, weight, quantity, date_purchased, description=''):
    self.name = name
    self.description = description
    self.weight = weight
    self.quantity = quantity
    self.date_purchased = date_purchased

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'weight': self.weight,
      'quantity': self.quantity,
      'date_purchased': self.date_purchased
    }

  def __repr__(self):
        return f'<Product {self.id}: {self.last_name}, {self.first_name}>'

