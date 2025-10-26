# event_alert_api.py
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so Streamlit frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect to SQLite
conn = sqlite3.connect("events.db", check_same_thread=False)
cursor = conn.cursor()

# Initialize table
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    description TEXT,
    event_date TEXT,
    notify_before_days INTEGER
)
""")
conn.commit()

# Pydantic model for incoming event
class Event(BaseModel):
    event_type: str
    description: str
    event_date: str
    notify_before_days: int

# POST /event - add a new event
@app.post("/event")
def add_event(event: Event):
    cursor.execute(
        "INSERT INTO events (event_type, description, event_date, notify_before_days) VALUES (?, ?, ?, ?)",
        (event.event_type, event.description, event.event_date, event.notify_before_days)
    )
    conn.commit()
    return {"message": "Event added successfully"}

# GET /upcoming - return all events with days_left
@app.get("/upcoming")
def get_upcoming_events():
    today = datetime.date.today()
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    rows = cursor.fetchall()
    events = []
    for e in rows:
        event_id, event_type, description, event_date_str, notify_days = e
        event_date = datetime.datetime.strptime(event_date_str, "%Y-%m-%d").date()
        days_left = (event_date - today).days
        events.append({
            "id": event_id,
            "event_type": event_type,
            "description": description,
            "event_date": event_date_str,
            "notify_before_days": notify_days,
            "days_left": days_left
        })
    return events
