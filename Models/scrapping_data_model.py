from pydantic import BaseModel
from typing import List

class ScrappingDataModel(BaseModel):
    url: str
    title: str
    address: str
    price: str
    price_per_m2: str
    description: str
    area: str
    rooms: str
    heating: str
    floor: str
    rent: str
    building_condition: str
    market: str
    ownership_form: str
    available_from: str
    offer_type: str
    additional_info: str

