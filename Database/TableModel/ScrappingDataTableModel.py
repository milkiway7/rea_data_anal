from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class scrapped_data_table(Base):
    
    __tablename__ = "ScrappedData"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CreatedAt = Column(DateTime, nullable=False)
    Url = Column(String(500), nullable=False)
    Title = Column(String(500), nullable=False)
    Address = Column(String(500), nullable=False)
    Price = Column(Numeric(15,2), nullable=False)
    PricePerM2 = Column(Numeric(10,2), nullable=False)
    Description = Column(Text, nullable=True)
    Area = Column(Numeric(10,2), nullable=True)
    Rooms = Column(String(500), nullable=True)
    Heating = Column(String(500), nullable=True)
    Floor = Column(String(500), nullable=True)
    Rent = Column(Numeric(15,2), nullable=True)
    BuildingCondition = Column(String(500), nullable=True)
    Market = Column(String(500), nullable=True)
    AvailableFrom = Column(String(500), nullable=True)
    OfferType = Column(String(500), nullable=True)
    AdditionalInfo = Column(Text, nullable=True)
    