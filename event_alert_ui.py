import streamlit as st
import pandas as pd
import requests
import datetime

# --- Page Config ---
st.set_page_config(page_title="Personal Event Reminder", page_icon="🎉", layout="wide")
st.title("🎉 Personal Event Reminder System")
st.write("Track birthdays, payments, anniversaries, and other important dates.")

# --- Backend API URLs (Render deployment) ---
API_BASE = "https://cloud-event-alert.onrender.com"  # your deployed backend URL
API_URL = f"{API_BASE}/event"        # POST/DELETE endpoint
UPCOMING_URL = f"{API_BASE}/upcoming"  # GET endpoint

# --- Custom CSS for Table Text ---
st.markdown("""
    <style>
    .stDataFrame thead, .stDataFrame tbody, .stDataFrame td, .stDataFrame th {
        color: black !important;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

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
                st.rerun()  # refresh UI immediately
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
            if event_filter != "All":
                events = [e for e in events if e["event_type"] == event_filter]
            return events
        else:
            st.error(f"❌ Failed to fetch events. Status Code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ Error connecting to backend: {e}")
        return []

# --- Function to delete an event ---
def delete_event(event_id):
    try:
        delete_url = f"{API_URL}/{event_id}"
        response = requests.delete(delete_url)
        if response.status_code == 200:
            st.success(f"🗑️ Event ID {event_id} deleted successfully!")
            st.rerun()
        else:
            st.error(f"❌ Failed to delete event {event_id}. Status Code: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Error deleting event: {e}")

# --- Fetch events from backend ---
events = fetch_events()

# --- Display events ---
if events:
    df = pd.DataFrame(events)
    df["Days Left"] = df["days_left"]

    st.subheader("📅 Upcoming Events")

    for _, row in df.iterrows():
        # Define color based on urgency
        if row["Days Left"] == 0:
            bg_color = "#ffcccc"
        elif row["Days Left"] <= 3:
            bg_color = "#fff3cd"
        else:
            bg_color = "#d4edda"

        with st.container():
            st.markdown(
                f"""
                <div style='background-color:{bg_color}; color:black; padding:15px; border-radius:10px; margin-bottom:10px;'>
                    <b>📌 {row['event_type']}</b>: {row['description']}<br>
                    📅 <b>Date:</b> {row['event_date']} | ⏳ <b>Days Left:</b> {row['Days Left']}
                </div>
                """,
                unsafe_allow_html=True
            )
            delete_col = st.columns([0.8, 0.2])[1]
            with delete_col:
                if st.button(f"🗑️ Delete {row['id']}", key=row['id']):
                    delete_event(row["id"])

else:
    st.info("No upcoming events found. Add some events to start receiving reminders!")
