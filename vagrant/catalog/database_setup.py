# Configuration code for ORM
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Class definition
class Category(Base):
    # Table definition
    __tablename__ = 'category'

    # Mapper information
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

# Class definition
class Item(Base):
    # Table definition
    __tablename__ = 'item'

    # Mapper information
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500))
    timestamp = Column(String(250), nullable=False)
    #added_by = Column(String(500))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

# Configuration code for ORM 
engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)