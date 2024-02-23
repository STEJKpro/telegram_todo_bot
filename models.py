from sqlalchemy import (
    Identity, create_engine, MetaData, Table, Integer, String,
    Column, DateTime, ForeignKey, Numeric,
    UniqueConstraint, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True, nullable=False)
    chat_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    username = Column(String(100), nullable=True)
    
    __table_args__ = (
            UniqueConstraint('name', 'surname',  name='unique_user'),         
        )

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    
    author_id = Column(Integer, ForeignKey('users.chat_id'))
    executor_id = Column(Integer, ForeignKey('users.chat_id'))
    discription = Column(String(100), nullable=False)
    priority = Column(String(25), nullable=False)
    deadline = Column(DateTime)
    status = Column(String(200), nullable=False)
    file = Column(JSON, nullable=True)