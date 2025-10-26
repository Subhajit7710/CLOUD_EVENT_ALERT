import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import datetime

st.set_page_config(page_title="Personal Event Reminder", page_icon="🎉", layout="wide")
st.title("🎉 Personal Event Reminder System")
st.write("Track birthdays, payments, anniversaries, and other important dates.")

# Auto-refresh every 10 seconds
st_autorefresh(interval=10_000, key="refresh")

# Connect to SQLite
conn = sqlite3.connect('events.db', check_same_thread=False)
cursor = conn.cursor()

# --- Add New Event Form ---
st.sidebar.header("➕ Add New Event")
with st.sidebar.form(key='add_event_form'):
    event_type = st.selectbox("Event Type:", ["Birthday", "Payment", "Anniversary", "Other"])
    description = st.text_input("Description / Name:")
    event_date = st.date_input("Event Date:")
    notify_days = st.number_input("Notify Before Days:", min_value=0, max_value=30, value=1)
    submit_button = st.form_submit_button(label="Add Event")

    if submit_button:
        cursor.execute(
            "INSERT INTO events (event_type, description, event_date, notify_before_days) VALUES (?, ?, ?, ?)",
            (event_type, description, event_date.strftime("%Y-%m-%d"), notify_days)
        )
        conn.commit()
        st.success(f"✅ Event '{description}' added successfully!")

# --- Sidebar Filter ---
event_filter = st.sidebar.selectbox("🔍 Filter by Event Type for Dashboard:", ("All", "Birthday", "Payment", "Anniversary", "Other"))

# --- Load events ---
if event_filter == "All":
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
else:
    cursor.execute("SELECT * FROM events WHERE event_type=? ORDER BY event_date ASC", (event_filter,))

rows = cursor.fetchall()
df = pd.DataFrame(rows, columns=["ID", "Event Type", "Description", "Event Date", "Notify Before Days"])

# --- Calculate days left ---
if not df.empty:
    today = datetime.date.today()
    df["Days Left"] = df["Event Date"].apply(lambda x: (datetime.datetime.strptime(x, "%Y-%m-%d").date() - today).days)

    # Highlight events that are today or upcoming soon
    def highlight_row(row):
        color = ""
        if row["Days Left"] == 0:
            color = "background-color: #ffcccc"  # Today = red
        elif row["Days Left"] <= 3:
            color = "background-color: #fff3cd"  # Soon = yellow
        else:
            color = "background-color: #d4edda"  # Later = green
        return [color] * len(row)

    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)
else:
    st.info("No events found. Add some events to start receiving reminders!")
