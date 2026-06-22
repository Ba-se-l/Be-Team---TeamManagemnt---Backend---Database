from sqlalchemy import create_engine

from src.database.base import Base

engine = create_engine("sqlite:///test.db", echo=True)

def create_database():
    Base.metadata.create_all(bind=engine)
    