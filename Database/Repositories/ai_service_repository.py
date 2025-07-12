from Database.database import Database
from sqlalchemy.future import select
from Database.TableModel.ScrappingDataTableModel import scrapped_data_table
from Database.TableModel.LastEmbeddedItemTableModel import LastEmbeddedItemTableModel
from Helpers.logger import get_logger
from sqlalchemy import text

class AiServiceRepository:
    def __init__(self):
        self.database = Database()
        self.logger = get_logger(self.__class__.__name__)
    
    async def remove_duplicates(self):
        try:
            async with self.database.get_session() as session:
                self.logger.info("Removing duplicates from scrapped_data_table")
                delete_duplicates_query = text("""
                    WITH DuplicateUrls AS (
                        SELECT 
                            [Id],
                            [Url],
                            ROW_NUMBER() OVER (PARTITION BY [Url] ORDER BY [Id] DESC) AS rn
                        FROM ScrappedData
                    )
                    DELETE FROM ScrappedData
                    WHERE [Id] IN (SELECT [Id] FROM DuplicateUrls WHERE rn > 1)""")
                await session.execute(delete_duplicates_query)
                await session.commit()
                self.logger.info("Duplicates removed successfully")
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {e}")
            raise

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
                    # Get the next 100 items after the last embedded item to LastEmbeddedItemTableModel table
                    query = select(scrapped_data_table).order_by(scrapped_data_table.Id).limit(100)
                    if last_item_id:
                         query = query.where(scrapped_data_table.Id > last_item_id)
                    result = await session.execute(query)
                    items = result.scalars().all()
                    
                    self.logger.info(f"Fetched {len(items)} items for embedding")
                    # add last embedded item URL to 
                    url_to_save = items[-1].Url if items else None
                    if url_to_save:
                        self.logger.info(f"Saving last embedded item URL: {url_to_save}")
                        await self.save_last_embedded_item_url(url_to_save)
                    return items
            except Exception as e:
                self.logger.error(f"Error fetching data for embedding: {e}")
                raise
            
    async def save_last_embedded_item_url(self, url: str):
        if not url:
            self.logger.warning("Tried to save empty URL, skipping.")
            return
        try:
            async with self.database.get_session() as session:
                self.logger.info(f"Saving last embedded item URL: {url}")
                last_embedded_item = LastEmbeddedItemTableModel(LastEmbeddedUrl=url)
                session.add(last_embedded_item)
                await session.commit()
                self.logger.info("Last embedded item saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving last embedded item: {e}")
            raise
