from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.config import settings 

class Base(DeclarativeBase):
    pass 


engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
)



SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session
)


