from fastapi import FastAPI, Body
from typing import List
from Models.scrapping_data_model import ScrappingDataModel
from Services.prepare_data import PrepareData
from contextlib import asynccontextmanager
from Database.database_init import initialize_database
from Helpers.logger import get_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await initialize_database()
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
        return {"msg": "Error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

