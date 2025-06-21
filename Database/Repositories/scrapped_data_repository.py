from datetime import datetime
from sqlalchemy.future import select
from Database.database import Database
from Database.TableModel.ScrappingDataModelDb import scrapped_data_table
from Helpers.logger import get_logger
from Database.Mappers.ScrappedDataMapper import ScrappedDataMapper

class ScrappedDataRepository(): 
    def __init__(self):
        self.database = Database()
        self.logger = get_logger(self.__class__.__name__)

    async def save_data(self, data):
        async with self.database.get_session() as session:
            try:
                data_urls = [item["url"] for item in data]
                existing_urls = (
                    await session.execute(select(scrapped_data_table.Url).where(scrapped_data_table.Url.in_(data_urls)))
                ).scalars().all()
                filtered_data = [item for item in data if item["url"] not in existing_urls]

                records = [ScrappedDataMapper.map_to_db_model(item) for item in filtered_data]
                session.add_all(records)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error saving data: {e}")