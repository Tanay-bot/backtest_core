# fetching candles from the LSE api

import pandas as pd
from key import API_KEY
from lse import LSE

from config import SYMBOL, INTERVAL, START


def load_candles():
    client = LSE(api_key=API_KEY)
    candles = client.candles(SYMBOL, INTERVAL, start=START)
    print("got", len(candles), "daily candles")
    df = pd.DataFrame(candles)
    return df.sort_values("timestamp").reset_index(drop=True)
