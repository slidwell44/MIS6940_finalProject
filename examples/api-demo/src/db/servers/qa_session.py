from sqlalchemy.orm import sessionmaker, Session

from .wlqadbsrv import get_engine

qa = get_engine()
engine = qa.engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_qa_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
