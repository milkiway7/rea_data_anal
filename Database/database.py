from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_CONFIG
from Helpers.logger import get_logger
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.engine = create_async_engine(
            os.getenv("DB_CONNECTION_STRING"),
            echo=True,
            fast_executemany=True,
            pool_size=10,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            connect_args={"timeout": 15} 
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def get_session(self):
        try:    
            return self.SessionLocal()
        except Exception as e:
            get_logger(self.__class__.__name__).error(f"Error creating session: {e}")

            