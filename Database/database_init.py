from Database.database import Database
from Database.TableModel.ScrappingDataTableModel import Base
from Database.TableModel.LastEmbeddedItemTableModel import Base 
from Database.TableModel.ScrappingDataArchiveTableModel import Base
from Helpers.logger import get_logger

async def initialize_database():
    try:
        db = Database()
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        get_logger().info("Database initialized successfully.")
    except Exception as e:
        get_logger().error(f"Database initialization failed: {e}")
