from fastapi import FastAPI, Request
import sqlite3
import datetime
import os
import requests

app = FastAPI()

# Connect to SQLite
conn = sqlite3.connect('events.db', check_same_thread=False)
cursor = conn.cursor()

# Add a new event
@app.post("/event")
async def add_event(request: Request):
    data = await request.json()
    event_type = data.get("event_type", "General")
    description = data.get("description", "No description")
    event_date = data.get("event_date")  # Format: YYYY-MM-DD
    notify_before_days = data.get("notify_before_days", 1)

    cursor.execute(
        "INSERT INTO events (event_type, description, event_date, notify_before_days) VALUES (?, ?, ?, ?)",
        (event_type, description, event_date, notify_before_days)
    )
    conn.commit()
    return {"status": "Event added", "event": data}

# Fetch upcoming events for today or next few days
@app.get("/upcoming")
async def upcoming_events():
    today = datetime.date.today()
    cursor.execute("SELECT * FROM events")
    all_events = cursor.fetchall()
    upcoming = []
    for e in all_events:
        event_id, event_type, description, event_date_str, notify_before_days = e
        event_date = datetime.datetime.strptime(event_date_str, "%Y-%m-%d").date()
        delta_days = (event_date - today).days
        if 0 <= delta_days <= notify_before_days:
            upcoming.append({
                "event_type": event_type,
                "description": description,
                "event_date": event_date_str,
                "days_left": delta_days
            })
    return upcoming
