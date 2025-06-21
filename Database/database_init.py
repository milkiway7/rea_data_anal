from Database.database import Database
from Database.TableModel.ScrappingDataModelDb import scrapped_data_table
from Helpers.logger import get_logger

async def initialize_database():
    try:
        db = Database()
        async with db.engine.begin() as conn:
            await conn.run_sync(scrapped_data_table.metadata.create_all)
        get_logger().info("Database initialized successfully.")
    except Exception as e:
        get_logger().error(f"Database initialization failed: {e}")
