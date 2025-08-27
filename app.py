import streamlit as st
import requests
import json
import csv
import os
import pandas as pd
from datetime import datetime

# --- API CONFIG ---
URL = "https://grpc-prod.orange.sixt.com/com.sixt.service.rent_booking.api.BookingService/GetBookingById"
PAYLOAD = {
    "booking_id": "fd520a9e-c874-49de-b3ac-630b0caff0ad",
    "currency": "CHF"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://www.sixt.ch",
    "Referer": "https://www.sixt.ch/",
    "x-client-id": "web-browser-2501006464537361390005373641050168024",
    "x-client-type": "web",
    "x-sx-tenant": "6"
}
LOG_FILE = "price_log.csv"


# --- FUNCTIONS ---
def fetch_price():
    resp = requests.post(URL, headers=HEADERS, json=PAYLOAD)
    data = resp.json()
    total_price = data["booking"]["selected"]["total"]["gross"]["value"]
    daily_price = total_price / 7
    return total_price, daily_price


def log_price(total, daily):
    today = datetime.now().strftime("%Y-%m-%d")
    # append to CSV
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([today, total, daily])


def load_log():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["date", "total_price", "daily_price"])
    return pd.read_csv(LOG_FILE, names=["date", "total_price", "daily_price"])


# --- STREAMLIT UI ---
st.set_page_config(page_title="Sixt Price Tracker", layout="centered")

st.title("Car Rental Price Tracker")

# fetch live price
try:
    total_price, daily_price = fetch_price()
    st.metric("Current Total Price (CHF)", f"{total_price:.2f}")
    st.metric("Current Daily Price (CHF)", f"{daily_price:.2f}")

    # log today's price
    log_price(total_price, daily_price)
except Exception as e:
    st.error(f"Failed to fetch price: {e}")

# load history
df = load_log()

if not df.empty:
    st.subheader("📊 Price History")
    st.line_chart(df.set_index("date")[["total_price", "daily_price"]])
    st.dataframe(df)
else:
    st.info("No price history yet.")
