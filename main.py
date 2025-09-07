from dotenv import load_dotenv
load_dotenv()
import uvicorn
from fastapi import FastAPI, Body
from typing import List
from Models.scrapping_data_model import ScrappingDataModel
from Services.prepare_data import PrepareData
from Database.Repositories.ai_service_repository import AiServiceRepository
from contextlib import asynccontextmanager 
from Helpers.initialize_db_with_retry import initialize_db_with_retry
from Helpers.logger import get_logger
from Database.Repositories.charts_repository import ChartsRepository
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from Database.Repositories.scrapped_data_repository import ScrappedDataRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await initialize_db_with_retry()
        yield
    except Exception as e:
        get_logger().error(f"Database initialisation failed: {e}")
  
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.delete("/clear_scrapped_data")
async def clear_scrapped_data():
    try:
        get_logger().info("Clearing scrapped data from database api reqest")
        scrapped_data_repo = ScrappedDataRepository()
        await scrapped_data_repo.clear_scrapped_data_and_archive()
    except Exception as e:
        get_logger().error(f"Error clearing scrapped data: {e}")
        return {"msg": "Error", "error": str(e)}

@app.post("/mark_soldout_for_nulls_scrapped_archive")
async def mark_soldout_for_nulls_scrapped_archive():
    try:
        get_logger().info("Marking SoldOut for nulls in ScrappedDataArchive")
        scrapped_data_repo = ScrappedDataRepository()
        result = await scrapped_data_repo.mark_soldout_for_nulls_scrapped_archive()
        return result
    except Exception as e:
        get_logger().error(f"Error marking SoldOut for nulls: {e}")
        return {"msg": "Error", "error": str(e)}

@app.post("/analyze")
async def analyze(data: List[ScrappingDataModel] = Body(...)):
    try:
        prepare_data = PrepareData(data)
        result = await prepare_data.prepare_data()
        return result
    except Exception as e:
        get_logger().error(f"Error during data analysis: {e}")
        return {"msg": "Error", "error": str(e)}
    
@app.patch("/remove_duplicates")
async def remove_duplicates():
    try:
        get_logger().info("Removing duplicates from scrapped data")
        ai_service_repo = AiServiceRepository()
        await ai_service_repo.remove_duplicates()  # This method will handle the removal of duplicates
        return {"msg": "Duplicates removed successfully"}
    except Exception as e:
        get_logger().error(f"Error removing duplicates: {e}")
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

@app.get("/median_price_per_m2")
async def median_price_per_m2():
    try:
        get_logger().info("Fetching data analysis results")
        charts_repository = ChartsRepository()
        median_price_per_m2 = await charts_repository.get_median_price_per_m2()
        return {"status":"Success","median_price_per_m2": median_price_per_m2}
    except Exception as e:
        get_logger().error(f"Error fetching data analysis results: {e}")
        return {"status": "Error", "error": str(e)}
    
@app.get("/price_distribution_per_m2")
async def price_distribution_per_m2():
    try:
        get_logger().info("Fetching price distribution per m2")
        charts_repository = ChartsRepository()
        price_distribution = await charts_repository.get_price_distribution_per_m2()
        return {"status": "Success", "price_distribution_per_m2": price_distribution}
    except Exception as e:
        get_logger().error(f"Error fetching price distribution per m2: {e}")
        return {"status": "Error", "error": str(e)}

@app.get("/area_dependency_on_price_per_m2")
async def area_dependency_on_price_per_m2(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sample_modulo: int = 10,
    top_n: int = 500):
    try:
        get_logger().info("Fetching area dependency on price per m2")
        charts_repository = ChartsRepository()
        area_dependency_on_price_per_m2 = await charts_repository.get_area_dependency_on_price_per_m2(
            start_date=start_date,
            end_date=end_date,
            sample_modulo=sample_modulo,
            top_n=top_n
        )
        return {"status": "Success", "area_dependency_on_price_per_m2": area_dependency_on_price_per_m2}
    except Exception as e:
        get_logger().error(f"Error fetching area dependency on price per m2: {e}")
        return {"status": "Error", "error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)


