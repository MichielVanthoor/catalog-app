#!/usr/bin/env python

"""
    This module initializes an sqlite database and
    creates the User, Category and Item tables and columns within it.

    __author__ = "Michiel Vanthoor"
    __version__ = "1.0"
    __date__ = "06/03/2018"

"""


# Import dependencies for ORM
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Class that defines the parameters for the User table"""
    # Table definition
    __tablename__ = 'user'

    # Mapper information
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """Class that defines the parameters for the Category table"""
    # Table definition
    __tablename__ = 'category'

    # Mapper information
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Item(Base):
    """Class that defines the parameters for the Item table"""
    # Table definition
    __tablename__ = 'item'

    # Mapper information
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500))
    timestamp = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'timestamp': self.timestamp
        }


# Configuration code for ORM
engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
