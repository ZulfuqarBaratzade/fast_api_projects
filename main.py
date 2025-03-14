from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
from pydantic import BaseModel
import os

app = FastAPI()

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Model for POST request
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# Get request for homepage
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("todolist.html", {"request": request})

# Post request to add items
@app.post("/add")
async def create_item(item: Item):
    item_dict = item.dict()

    # JSON faylını oxuyub list şəklində saxlamaq
    if os.path.exists("database.json"):
        with open("database.json", "r") as f:
            try:
                items = json.load(f)
            except json.JSONDecodeError:
                items = []
    else:
        items = []

    # Yeni item əlavə etmək
    items.append(item_dict)

    # JSON faylını yeniləmək
    with open("database.json", "w") as f:
        json.dump(items, f, indent=4)

    return item_dict

# DELETE request for deleting an item
@app.delete("/delete/{name}")
async def delete_item(name: str):
    if not os.path.exists("database.json"):
        raise HTTPException(status_code=404, detail="Database not found")

    with open("database.json", "r") as f:
        try:
            items = json.load(f)
        except json.JSONDecodeError:
            items = []

    filtered_items = [item for item in items if item["name"] != name]

    if len(filtered_items) == len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    with open("database.json", "w") as f:
        json.dump(filtered_items, f, indent=4)

    return {"message": f"Item '{name}' deleted successfully"}
