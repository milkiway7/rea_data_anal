from Database.TableModel.ScrappingDataTableModel import scrapped_data_table
from datetime import datetime

class ScrappedDataMapper:
    @staticmethod
    def map_to_db_model(data):
        return scrapped_data_table(
            Url=data.get("url"),
            CreatedAt= datetime.now(),
            Title=data.get("title"),
            Address=data.get("address"),
            Price=data.get("price"),
            PricePerM2=data.get("price_per_m2"),
            Description=data.get("description"),
            Area=data.get("area"),
            Rooms=data.get("rooms"),
            Heating=data.get("heating"),
            Floor=data.get("floor"),
            Rent=data.get("rent"),
            BuildingCondition=data.get("building_condition"),
            Market=data.get("market"),
            AvailableFrom=data.get("available_from"),
            OfferType=data.get("offer_type"),
            AdditionalInfo=data.get("additional_info")
        )