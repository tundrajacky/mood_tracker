import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Mood of the Queue", layout="centered")

# Auto-refresh every 60 seconds
st.markdown(
    """
    <meta http-equiv="refresh" content="60">
    """,
    unsafe_allow_html=True,
)

# Google Sheets Setup
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
CREDS_FILE = 'credentials.json'  # Json key file
SHEET_NAME = 'Mood Tracker'      # Google Sheet name

@st.cache_resource
def connect_gsheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

sheet = connect_gsheet()

# UI
st.title("🧠 Mood of the Queue")
mood = st.selectbox("How's the queue feeling?", ["😊", "😕","😠","😭"])

# Submit mood
if mood:
    note = st.text_input("Optional note")
    if st.button("Submit Mood"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([timestamp, mood, note])
        st.success("Mood recorded!")
# Visualization
records = sheet.get_all_records()

if records:
    df = pd.DataFrame(records)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    st.subheader("📅 Pick a date to view mood chart")
    selected_date = st.date_input("Date", datetime.today().date())

    df_selected = df[df['timestamp'].dt.date == selected_date]
    mood_counts = df_selected['mood'].value_counts()

    if not mood_counts.empty:
        st.subheader("📊 Mood Chart")
        fig, ax = plt.subplots()
        mood_counts.sort_index().plot(kind='bar', ax=ax)
        ax.set_ylabel("Count")
        ax.set_xlabel("Mood")
        st.pyplot(fig)
    else:
        st.info("No moods recorded for this date.")
else:
    st.info("No moods logged yet.")

