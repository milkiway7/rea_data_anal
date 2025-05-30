from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class scrapped_data_table(Base):
    
    __tablename__ = "ScrappedData"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Url = Column(String(400), nullable=False)
    Title = Column(String(300), nullable=False)
    Address = Column(String(200), nullable=False)
    Price = Column(Numeric(10,2), nullable=False)
    PricePerM2 = Column(Numeric(10,2), nullable=False)
    Description = Column(Text, nullable=True)
    Area = Column(Numeric(4,2), nullable=True)
    Heating = Column(String(50), nullable=True)
    Floor = Column(String(50), nullable=True)
    Rent = Column(Numeric(10,2), nullable=True)
    BuildingCondition = Column(String(50), nullable=True)
    Market = Column(String(50), nullable=True)
    AvailableFrom = Column(String(50), nullable=True)
    AdditionalInfo = Column(Text, nullable=True)
    