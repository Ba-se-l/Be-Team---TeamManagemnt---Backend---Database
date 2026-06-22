from sqlalchemy.orm import Session

from src.database.init import engine

def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()