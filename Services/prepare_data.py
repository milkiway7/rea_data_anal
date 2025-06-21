import pandas as pd
from Database.Repositories.scrapped_data_repository import ScrappedDataRepository
import math
from Helpers.logger import get_logger

class PrepareData:
    def __init__(self,data):
        self.data = data
        self.df = None
        self.columns_to_float = [
            "price",
            "price_per_m2",
            "area",
            "rent"
        ]
        self.repository = ScrappedDataRepository()
        self.logger = get_logger(self.__class__.__name__)

    async def prepare_data(self):
        try:
            self.to_dataframe()
            self.clean_data()
            records_for_db = self.df.to_dict(orient='records')
            records_for_db = self.convert_to_float(records_for_db)
            records_for_db = self.nan_to_none(records_for_db)
            await self.repository.save_data(records_for_db)
        except Exception as e:
            self.logger.error(f"Error in prepare_data: {e}")
            
    
    def to_dataframe(self):
        try:
            data_dicts = [item.dict() for item in self.data]
            self.df = pd.DataFrame.from_records(data_dicts)
        except Exception as e:
            self.logger.error(f"Error converting data to DataFrame: {e}")
            
    
    def clean_data(self): 
        try:
            self.df = self.df.astype(str)

            self.df["price"] = self.df["price"].str.replace("zł","", regex=False).str.replace(" ", "", regex=False)
            self.df["price_per_m2"] = self.df["price_per_m2"].str.replace("zł/m²","", regex=False).str.replace(" ", "", regex=False)
            self.df["area"] =  self.df["area"].str.extract(r"(\d+(?:\.\d+)?)").astype(str)[0]
            self.df["rent"] = self.df["rent"].str.replace(" ","").str.extract(r"(\d+)").astype(str)[0]

            self.df = self.df.replace({r"\n": " ", r"\t": " ", r"\xa0": " "}, regex=True)
            self.df = self.df.replace(r"\s{2,}", " ", regex=True)
            self.df = self.df.replace("brak informacji", None)
        except Exception as e:
            self.logger.error(f"Error cleaning data: {e}")
            

    def convert_to_float(self,records_for_db):
        try:
            for record in records_for_db:
                for field in self.columns_to_float  :
                    if field in record:
                        try:
                            record[field] = float(record[field])
                        except ValueError:
                            record[field] = None
            return records_for_db
        except Exception as e:
            self.logger.error(f"Error converting columns to float: {e}")
            
    
    def nan_to_none(self, records):
        try:
            def convert_value(v):
                if isinstance(v, float) and math.isnan(v):
                    return None
                return v

            return [
                {k: convert_value(v) for k, v in record.items()}
                for record in records
            ]
        except Exception as e:
            self.logger.error(f"Error converting NaN to None: {e}")
            
        
