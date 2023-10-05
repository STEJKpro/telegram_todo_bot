from sqlalchemy import create_engine
from sqlalchemy.orm import Session
engine = create_engine("sqlite:///database.db", echo=True)
session= Session(engine)