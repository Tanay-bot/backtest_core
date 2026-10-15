# fetching candles from the LSE api

import pandas as pd
from key import API_KEY
from lse import LSE

from config import SYMBOL, INTERVAL, START

REQUIRED_COLS = ["timestamp", "open", "high", "low", "close", "volume"]


def validate(df):
    if len(df) == 0:
        raise ValueError("api returned zero candles")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError("api data missing columns: " + ", ".join(missing))

    dupes = df["timestamp"].duplicated().sum()
    if dupes > 0:
        raise ValueError("api data has " + str(dupes) + " duplicate timestamps")

    # daily bars should arrive in order, oldest first
    ts = pd.to_datetime(df["timestamp"])
    if not ts.is_monotonic_increasing:
        raise ValueError("api data timestamps are out of order")

    # biggest gap between two bars should stay close to one day
    # the api has real holes (jul 2024, dec 2024) so big gaps only warn
    diffs = ts.diff().dropna()
    biggest_gap = diffs.max().total_seconds() / 86400
    if biggest_gap > 3:
        print("warning: gap in data:", round(biggest_gap, 1), "days between bars")


def load_candles():
    client = LSE(api_key=API_KEY)
    candles = client.candles(SYMBOL, INTERVAL, start=START)

    df = pd.DataFrame(candles)
    validate(df)

    print("got", len(df), "daily candles")
    return df.sort_values("timestamp").reset_index(drop=True)
