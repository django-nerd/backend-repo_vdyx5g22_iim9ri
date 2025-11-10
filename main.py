import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date

from database import db, create_document, get_documents
from schemas import Booking

app = FastAPI(title="Achyuth Hotels API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookingRequest(Booking):
    pass

class BookingResponse(BaseModel):
    id: str

@app.get("/")
def read_root():
    return {"message": "Achyuth Hotels API running"}

@app.get("/test")
def test_database():
    info = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            info["database"] = "✅ Available"
            info["database_url"] = "✅ Set"
            info["database_name"] = getattr(db, 'name', '✅ Connected')
            info["connection_status"] = "Connected"
            try:
                info["collections"] = db.list_collection_names()[:10]
                info["database"] = "✅ Connected & Working"
            except Exception as e:
                info["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        info["database"] = f"❌ Error: {str(e)[:80]}"
    import os
    if os.getenv("DATABASE_URL"): info["database_url"] = "✅ Set"
    if os.getenv("DATABASE_NAME"): info["database_name"] = "✅ Set"
    return info

@app.post("/api/book", response_model=BookingResponse)
def create_booking(payload: BookingRequest):
    try:
        booking_id = create_document("booking", payload)
        return {"id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms")
def list_rooms():
    rooms = [
        {
            "slug": "deluxe-king",
            "name": "Deluxe King Room",
            "price": 5499,
            "description": "Spacious room with premium linens and city view",
            "amenities": ["AC", "Wi‑Fi", "Breakfast", "Smart TV", "Mini Bar", "Work Desk"],
            "image": "/hero-deluxe.svg"
        },
        {
            "slug": "premium-suite",
            "name": "Premium Suite",
            "price": 8999,
            "description": "Suite with living area, balcony and luxury bath",
            "amenities": ["AC", "Wi‑Fi", "Breakfast", "Bathtub", "Balcony", "24x7 Service"],
            "image": "/hero-suite.svg"
        },
        {
            "slug": "twin-classic",
            "name": "Classic Twin",
            "price": 4499,
            "description": "Comfortable twin beds, ideal for friends or colleagues",
            "amenities": ["AC", "Wi‑Fi", "Breakfast", "Smart TV", "Wardrobe", "Room Service"],
            "image": "/hero-twin.svg"
        }
    ]
    return rooms

@app.get("/schema")
def get_schema():
    return {
        "booking": Booking.model_json_schema()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
