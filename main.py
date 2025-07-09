from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Body
from typing import List
from Models.scrapping_data_model import ScrappingDataModel
from Services.prepare_data import PrepareData
from Database.Repositories.ai_service_repository import AiServiceRepository
from contextlib import asynccontextmanager 
from Helpers.initialize_db_with_retry import initialize_db_with_retry
from Helpers.logger import get_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await initialize_db_with_retry()
        yield
    except Exception as e:
        get_logger().error(f"Database initialisation failed: {e}")
  
app = FastAPI(lifespan=lifespan)

@app.post("/analyze")
async def analyze(data: List[ScrappingDataModel] = Body(...)):
    try:
        prepare_data = PrepareData(data)
        await prepare_data.prepare_data()
        return {"msg": "Ok"}
    except Exception as e:
        get_logger().error(f"Error during data analysis: {e}")
        return {"msg": "Error", "error": str(e)}

@app.get("/get_data_for_embedding")
async def get_data_for_embedding():
    try:
        get_logger().info("Fetching data for embedding from database")
        ai_service_repo = AiServiceRepository()
        items = await ai_service_repo.get_data_for_embedding()
        return {"items": items}
    except Exception as e:
        get_logger().error(f"Error fetching data for embedding: {e}")
        return {"msg": "Error", "error": str(e)}

        
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)


