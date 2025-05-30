from Database.database import Database
from Database.TableModel.scrapped_data_table import scrapped_data_table
from Helpers.logger import get_logger

async def initialize_database():
    logger = get_logger()
    logger.info("Initializing database...")
    db = Database()
    async with db.engine.begin() as conn:
        await conn.run_sync(scrapped_data_table.metadata.create_all)
    logger.info("Database initialized successfully.")
