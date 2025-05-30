from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_CONFIG

class Database:
    def __init__(self):
        self.engine = create_async_engine(
            f"mssql+aioodbc://{DATABASE_CONFIG['server']}/{DATABASE_CONFIG['database']}?driver={DATABASE_CONFIG['driver']}&trusted_connection={DATABASE_CONFIG['trusted_connection']}",
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
        return self.SessionLocal()