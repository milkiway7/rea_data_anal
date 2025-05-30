from fastapi import FastAPI, Request, Body
from typing import List
from Models.scrapping_data_model import ScrappingDataModel
from Modules.prepare_data import PrepareData
from contextlib import asynccontextmanager
from Database.database_init import initialize_database



@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield
    
app = FastAPI(lifespan=lifespan)

@app.post("/analyze")
async def analyze(data: List[ScrappingDataModel] = Body(...)):
    # for item in data:
    #     print(f"Title: {item.title}, Price: {item.price}")
    prepare_data = PrepareData(data)
    prepare_data.prepare_data()
    return {"msg": "Ok"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)

