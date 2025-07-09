from Database.database import Database
from sqlalchemy.future import select
from Database.TableModel.ScrappingDataTableModel import scrapped_data_table
from Database.TableModel.LastEmbeddedItemTableModel import LastEmbeddedItemTableModel
from Helpers.logger import get_logger


class AiServiceRepository:
    def __init__(self):
        self.database = Database()
        self.logger = get_logger(self.__class__.__name__)
    
    async def get_first_item(self): 
        async with self.database.get_session() as session:
            try:
                self.logger.info("Fetching first item from LastEmbeddedItemTableModel")
                result = await session.execute(select(LastEmbeddedItemTableModel.LastEmbeddedUrl)
                                               .order_by(LastEmbeddedItemTableModel.Id.desc())
                                               .limit(1))
                item = result.scalars().first()
                self.logger.info(f"First item fetched: {item}")
                return item
            except Exception as e:
                self.logger.error(f"Error fetching first item: {e}")

    async def get_data_for_embedding(self):
            try:
                self.logger.info("Fetching data for embedding from scrapped_data_table")
                last_item_url = await self.get_first_item()
                last_item_id = None
                async with self.database.get_session() as session:
                    if last_item_url:
                        self.logger.info(f"Fetching Id for last embedded Url: {last_item_url}")
                        # Fetch the Id for the last embedded URL from scrapped_data_table
                        result = await session.execute(
                               select(scrapped_data_table.Id)
                               .where(scrapped_data_table.Url == last_item_url)
                        )
                        last_item_id = result.scalars().first()
                        self.logger.info(f"Last embedded Id found: {last_item_id}")
                    else:
                          self.logger.info("No last embedded URL found")
                    # Get the next 100 items after the last embedded item
                    query = select(scrapped_data_table).order_by(scrapped_data_table.Id).limit(100)
                    if last_item_id:
                         query = query.where(scrapped_data_table.Id > last_item_id)
                    result = await session.execute(query)
                    items = result.scalars().all()
                    self.logger.info(f"Fetched {len(items)} items for embedding")
                    return items
            except Exception as e:
                self.logger.error(f"Error fetching data for embedding: {e}")
                raise
            
                    
