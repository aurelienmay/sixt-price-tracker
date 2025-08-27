import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

from functions import log_price, load_log, color_deltas

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


# --- FUNCTIONS ---
def fetch_price():
    resp = requests.post(URL, headers=HEADERS, json=PAYLOAD)
    data = resp.json()
    total_price = round(data["booking"]["selected"]["total"]["gross"]["value"], 2)
    daily_price = round(total_price / 7, 2)  # 7 days rental
    return total_price, daily_price


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
# Compute delta compared to previous row
df["total_delta"] = df["total_price"].diff()
df["daily_delta"] = df["daily_price"].diff()

# Optional: fill NaN for first row with 0
df["total_delta"] = df["total_delta"].fillna(0)
df["daily_delta"] = df["daily_delta"].fillna(0)

if not df.empty:
    st.subheader("📊 Price History")
    st.line_chart(df.set_index("date")[["total_price", "daily_price"]])
    # Apply coloring only to delta columns
    styled_df = (
        df.style
        .format("{:.2f}", subset=["total_price", "daily_price", "total_delta", "daily_delta"])
        .applymap(color_deltas, subset=["total_delta", "daily_delta"])
    )
    # Show in Streamlit
    st.dataframe(styled_df)
else:
    st.info("No price history yet.")
