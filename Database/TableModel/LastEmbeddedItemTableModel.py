from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class LastEmbeddedItemTableModel(Base):

    __tablename__ = "LastEmbeddedItem"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    LastEmbeddedUrl = Column(String(500), nullable=False)

    