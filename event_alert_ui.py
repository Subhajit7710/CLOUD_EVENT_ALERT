import streamlit as st
import pandas as pd
import requests
import datetime

# --- Page Config ---
st.set_page_config(page_title="Personal Event Reminder", page_icon="🎉", layout="wide")
st.title("🎉 Personal Event Reminder System")
st.write("Track birthdays, payments, anniversaries, and other important dates.")

# --- Backend API URLs (Render deployment) ---
API_URL = " https://cloud-event-alert.onrender.com/event"      # POST to add new events
UPCOMING_URL = " https://cloud-event-alert.onrender.com/upcoming"  # GET upcoming events

# --- Sidebar: Add New Event ---
st.sidebar.header("➕ Add New Event")
with st.sidebar.form(key='add_event_form'):
    event_type = st.selectbox("Event Type:", ["Birthday", "Payment", "Anniversary", "Other"])
    description = st.text_input("Description / Name:")
    event_date = st.date_input("Event Date:")
    notify_days = st.number_input("Notify Before Days:", min_value=0, max_value=30, value=1)
    submit_button = st.form_submit_button(label="Add Event")

    if submit_button:
        payload = {
            "event_type": event_type,
            "description": description,
            "event_date": event_date.strftime("%Y-%m-%d"),
            "notify_before_days": notify_days
        }
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                st.success(f"✅ Event '{description}' added successfully!")
                events = requests.get(UPCOMING_URL).json()  # <-- immediately refresh events
            else:
                st.error(f"❌ Failed to add event. Status Code: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error connecting to backend: {e}")

# --- Sidebar: Event Filter ---
st.sidebar.header("🔍 Dashboard Filter")
event_filter = st.sidebar.selectbox("Filter by Event Type:", ("All", "Birthday", "Payment", "Anniversary", "Other"))

# --- Function to fetch events ---
def fetch_events():
    try:
        response = requests.get(UPCOMING_URL)
        if response.status_code == 200:
            events = response.json()
            # Filter events if needed
            if event_filter != "All":
                events = [e for e in events if e["event_type"] == event_filter]
            return events
        else:
            st.error(f"❌ Failed to fetch events. Status Code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ Error connecting to backend: {e}")
        return []

# --- Fetch events from backend ---
events = fetch_events()

# --- Debugging (optional) ---
st.write("DEBUG: Fetched Events:", events)

# --- Display events ---
if events:
    df = pd.DataFrame(events)
    df["Days Left"] = df["days_left"]

    # Highlight events based on urgency
    def highlight_row(row):
        if row["Days Left"] == 0:
            color = "background-color: #ffcccc"  # Today = red
        elif row["Days Left"] <= 3:
            color = "background-color: #fff3cd"  # Soon = yellow
        else:
            color = "background-color: #d4edda"  # Later = green
        return [color] * len(row)

    st.dataframe(
        df[["event_type", "description", "event_date", "Days Left"]].style.apply(highlight_row, axis=1),
        use_container_width=True
    )
else:
    st.info("No upcoming events found. Add some events to start receiving reminders!")
