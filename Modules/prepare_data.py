import pandas as pd

class PrepareData:
    def __init__(self,data):
        self.data = data
        self.df = None

    def prepare_data(self):
        self.to_dataframe()
        self.clean_data()

    def to_dataframe(self):
        data_dicts = [item.dict() for item in self.data]
        self.df = pd.DataFrame.from_records(data_dicts)
    
    def clean_data(self): 
        #map to string for specific columns 
        for column in self.df.columns:
            self.df[column] = self.df[column].astype(str)

        # self.df.replace("\xa0", "", regex=True).str.replace("\n", "", regex=False)  

        self.df["price"] = self.df["price"].str.replace("zł","", regex=False).str.replace(" ", "", regex=False)
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
        self.df["price_per_m2"] = self.df["price_per_m2"].str.replace("zł/m²","", regex=False).str.replace("zł/m2","",regex=False).str.replace(" ", "", regex=False)
        self.df["price_per_m2"] = pd.to_numeric(self.df["price_per_m2"], errors="coerce")
        self.df["area"] = self.df["area"].str.replace("m²","", regex=False).str.replace("m2","",regex=False).str.replace(" ", "", regex=False)
        self.df["area"] = pd.to_numeric(self.df["area"], errors="coerce")
        self.df["rent"] = self.df["rent"].str.replace("zł","", regex=False).str.replace(" ", "", regex=False)
        self.df["rent"] = pd.to_numeric(self.df["rent"], errors="coerce")
        print(self.df["price"].iloc[0])
        print(self.df["price_per_m2"].iloc[0])
        print(self.df["area"].iloc[0])
        print(self.df["rent"].iloc[0])
