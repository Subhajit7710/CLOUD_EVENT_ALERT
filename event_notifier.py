import sqlite3
import datetime
import time
from send_event import send_telegram, send_sms

conn = sqlite3.connect("events.db")
cursor = conn.cursor()

while True:
    today = datetime.date.today()
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    for e in rows:
        event_id, event_type, description, event_date_str, notify_days = e
        event_date = datetime.datetime.strptime(event_date_str, "%Y-%m-%d").date()
        if (event_date - today).days == notify_days:
            message = f"Reminder: {event_type} '{description}' is in {notify_days} day(s)!"
            send_telegram(message)
            # send_sms("+91XXXXXXXXXX", message)  # Uncomment & replace with real number
    time.sleep(3600)  # check every hour
