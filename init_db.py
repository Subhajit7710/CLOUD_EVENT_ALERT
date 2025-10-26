import sqlite3

# Connect to SQLite (file will be created automatically)
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Create table for personal events
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    description TEXT,
    event_date TEXT,
    notify_before_days INTEGER
)
''')

conn.commit()
conn.close()

print("✅ Personal events database created successfully!")
