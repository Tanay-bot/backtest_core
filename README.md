# BTC SMA Crossover Backtester

A portfolio backtesting engine for crypto, built from scratch in Python. It tests a classic strategy — buy when the 20-day SMA crosses above the 50-day SMA, sell when it crosses below — on daily BTC/USD candles from the [London Strategic Edge (LSE)](https://lse.dev) free API.

## What it does

- Fetches daily BTC/USD candles starting 2024-01-01
- Computes 20-day and 50-day simple moving averages on daily closes
- Enters long when the fast SMA is above the slow SMA (signal checked on the *previous* bar to avoid lookahead bias, fills at the *next* bar's open)
- Exits when the fast SMA falls back below the slow SMA
- Charges a 0.1% fee per trade
- Starts with $10,000 cash and reports total return, max drawdown, trade count, win rate, and a full trade log

## Quick start

```bash
pip install lse-data pandas
python3 main.py
```

You'll need an API key. Get a free one from LSE and drop it in a `key.py` file (gitignored):

```python
API_KEY = "your_key_here"
```

Sample output:

```
got 953 daily candles

===== RESULTS =====
total return: 113.29 %
max drawdown: 28.83 %
trades: 19
win rate: 66.7 % (of 9 sells)
final equity: $ 21329.36
```

## Project structure

```
├── config.py     # all tunable parameters in one place
├── data.py       # fetches + normalizes candles into a pandas DataFrame
├── engine.py     # the backtest loop, pure functions in / results out
├── main.py       # entrypoint, glues everything together
└── key.py        # API key (gitignored, create your own)
```



## Roadmap

- [ ] Buy-and-hold benchmark comparison
- [ ] Slippage modeling
- [ ] CAGR, Sharpe ratio, turnover, exposure metrics
- [ ] CSV data loading as an alternative to the API
- [ ] Multi-asset baskets
- [ ] Long/short support
- [ ] Automated tests + CI
