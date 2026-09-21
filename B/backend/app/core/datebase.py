# app/core/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase


import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "interview_business.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLite 必须加上 connect_args={"check_same_thread": False} 支持多线程
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明性基类"""
    pass

def get_db():
    """FastAPI 数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()