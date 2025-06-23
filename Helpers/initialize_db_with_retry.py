import asyncio
from Database.database_init import initialize_database
from Helpers.logger import get_logger

MAX_RETRIES = 10
RETRY_DELAY = 5  

async def initialize_db_with_retry():
    for attempt in range(MAX_RETRIES):
        try:
            get_logger().info(f"Attempting to initialize database (Attempt {attempt + 1}/{MAX_RETRIES})")
            await initialize_database()
            get_logger().info("Database initialized successfully.")
            return
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            get_logger().error(f"Database initialization failed on attempt {attempt + 1}: {e}")
            