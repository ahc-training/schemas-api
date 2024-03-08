from sqlalchemy import create_engine, Index, event
from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated, AsyncIterator
from fastapi import Depends
from datetime import datetime

INITIAL_DATA = {
      'users': [
            {
                  'username': 'vagrant',
                  'password': 'vagrant'
            }
      ]
}

class NotFoundError(Exception):
    pass

Base = declarative_base()

class DbSchema(Base):
    __tablename__ = "schemas"
    __table_args__ = (Index('idx_schemas', 'name', 'schema_type', unique=True, ),)
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    schema_type: Mapped[str] = mapped_column(nullable=False)
    data: Mapped[str] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    modifiedon: Mapped[datetime] = mapped_column(onupdate=datetime.now)

class DbUser(Base):
    __tablename__ = "users"
    __table_args__ = (Index("idx_users", 'username', unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)


def initialize_table(target, connection, **kw):
    tablename = str(target)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])

DATABASE_URL = "sqlite:////app/sqlite/schemas.db"

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0, pool_recycle=3600, pool_timeout=60)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
event.listen(DbUser.__table__, 'after_create', initialize_table)
Base.metadata.create_all(bind=engine)

async def get_db() -> AsyncIterator[Session]:
    database =  session_local()
    try:
        yield database
    finally:
        database.close()

db_dependency = Annotated[Session, Depends(get_db)]