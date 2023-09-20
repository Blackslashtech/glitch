import time
from fastapi import FastAPI

app = FastAPI()


items = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: str):
    time.sleep(5)
    try:
        return {"item": items[item_id]}
    except KeyError:
        return {"item": ""}

@app.post("/items/{item_id}/{item}")
def create_item(item_id: str, item: str):
    time.sleep(5)
    items[item_id] = item
    return {"item": item}
