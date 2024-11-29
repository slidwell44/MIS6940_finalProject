from sqlalchemy.orm import sessionmaker, Session

from .widevdbsrv import get_engine

dev = get_engine()
engine = dev.engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_dev_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
