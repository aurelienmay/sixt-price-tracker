from datetime import datetime
import pandas as pd
import csv
import os

LOG_FILE = "price_log.csv"

def log_price(total, daily):
    today = datetime.now().strftime("%Y-%m-%d")

    # if file doesn't exist, create it with header
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "total_price", "daily_price"])
            writer.writerow([today, total, daily])
        return

    # load existing log
    df = pd.read_csv(LOG_FILE)

    # check if today's date is already in the log
    if today in df["date"].values:
        # optional: update if price changed
        last_row = df[df["date"] == today].iloc[-1]
        if last_row["total_price"] != total:
            df.loc[df["date"] == today, ["total_price", "daily_price"]] = [total, daily]
            df.to_csv(LOG_FILE, index=False)
    else:
        # append new row
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([today, total, daily])

def load_log():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["date", "total_price", "daily_price"])
    
    return pd.read_csv(LOG_FILE)


# Define a function to color deltas
def color_deltas(val):
    if val < 0:
        return 'color: green'
    elif val > 0:
        return 'color: red'
    else:
        return ''  # no color for zero