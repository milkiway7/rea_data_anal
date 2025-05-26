from fastapi import FastAPI, Request, Body
from typing import List
from Models.scrapping_data_model import ScrappingDataModel

app = FastAPI()

@app.post("/analyze")
async def analyze(data: List[ScrappingDataModel] = Body(...)):
    # for item in data:
    #     print(f"Title: {item.title}, Price: {item.price}")
    a = data
    print(data)
    return {"msg": "Ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)