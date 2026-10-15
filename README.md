# BTC SMA Crossover Backtester

A portfolio backtesting engine for crypto, built from scratch in Python. It tests a classic strategy — buy when the 20-day SMA crosses above the 50-day SMA, sell when it crosses below — on daily BTC/USD candles from the [London Strategic Edge (LSE)](https://lse.dev) free API.

## What it does

- Fetches daily BTC/USD candles starting 2024-01-01 and validates them (no duplicates, no gaps, required columns present)
- Computes 20-day and 50-day simple moving averages on daily closes
- Enters long when the fast SMA is above the slow SMA (signal checked on the *previous* bar to avoid lookahead bias, fills at the *next* bar's open)
- Exits when the fast SMA falls back below the slow SMA, and closes any open position at the end of the test
- Charges a 0.1% fee per trade plus 10 bps slippage on fills
- Starts with $10,000 cash and reports total return, CAGR, max drawdown, Sharpe, exposure, round trips, win rate, and a full trade log

## Quick start

```bash
pip install -r requirements.txt
python3 main.py
```

You'll need an API key. Get a free one from LSE and drop it in a `key.py` file (gitignored):

```python
API_KEY = "your_key_here"
```

Sample output:

```
got 956 daily candles

===== RESULTS =====
total return: 105.19 %
cagr: 31.19 %
max drawdown: 29.12 %
sharpe: 1.03
exposure: 57.2 %
round trips: 10
win rate: 70.0 % (of 10 closed trades)
final equity: $ 20519.32
```

## Project structure

```
├── config.py        # all tunable parameters in one place
├── data.py          # fetches + validates candles into a pandas DataFrame
├── engine.py        # the backtest loop, pure functions in / results out
├── main.py          # entrypoint, glues everything together
├── requirements.txt # pinned dependencies
├── LICENSE          # MIT
└── key.py           # API key (gitignored, create your own)
```

## Roadmap

- [x] Slippage modeling
- [x] CAGR, Sharpe ratio, exposure metrics
- [x] Close open position at end of test
- [x] Data validation
- [ ] Buy-and-hold benchmark comparison
- [ ] Turnover metric
- [ ] CSV data loading as an alternative to the API
- [ ] Multi-asset baskets
- [ ] Long/short support
- [ ] Automated tests + CI
