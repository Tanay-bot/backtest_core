# sma crossover backtest engine

import math

import pandas as pd

# run the backtest, returns dict with results and trade log
# slippage_bps makes fills worse than the bar price, in basis points
def run_backtest(df, fast, slow, fee, slippage_bps, starting_cash):
    df["sma_fast"] = df["close"].rolling(fast).mean()
    df["sma_slow"] = df["close"].rolling(slow).mean()

    slip = slippage_bps / 10000.0

    cash = starting_cash
    coins = 0.0
    last_buy_price = 0.0
    last_buy_cost = 0.0
    wins = 0
    sells = 0
    round_trips = 0
    bars_in_market = 0

    equity_values = []
    trades = []

    # warm up: first slow-window bars have nan smas, nothing to trade yet
    warmup = slow

    # signal from previous bar, no lookahead
    for i in range(warmup, len(df)):
        if df["sma_fast"].iloc[i - 1] > df["sma_slow"].iloc[i - 1]:
            target = 1
        else:
            target = 0

        # buys fill above the open, sells fill below it
        open_price = df["open"].iloc[i]
        if target == 1:
            fill_price = open_price * (1 + slip)
        else:
            fill_price = open_price * (1 - slip)

        if coins > 0:
            bars_in_market = bars_in_market + 1

        if target == 1 and coins == 0:
            coins = (cash * (1 - fee)) / fill_price
            last_buy_price = fill_price
            last_buy_cost = cash  # cash spent at entry, fees included
            trades.append({"date": df["timestamp"].iloc[i], "side": "BUY", "price": round(fill_price, 2), "coins": round(coins, 6)})
            cash = 0.0
        elif target == 0 and coins > 0:
            proceeds = coins * fill_price * (1 - fee)
            if proceeds > last_buy_cost:
                wins = wins + 1
            sells = sells + 1
            round_trips = round_trips + 1
            trades.append({"date": df["timestamp"].iloc[i], "side": "SELL", "price": round(fill_price, 2), "cash_out": round(proceeds, 2)})
            coins = 0.0
            cash = proceeds

        equity_values.append(cash + coins * df["close"].iloc[i])

    # close any open position at the last close so the
    # metrics and equity curve describe the same set of trades
    if coins > 0:
        last_close = df["close"].iloc[len(df) - 1]
        proceeds = coins * last_close * (1 - fee)
        if proceeds > last_buy_cost:
            wins = wins + 1
        sells = sells + 1
        round_trips = round_trips + 1
        cash = proceeds
        coins = 0.0
        trades.append({"date": df["timestamp"].iloc[len(df) - 1], "side": "SELL", "price": round(last_close, 2), "cash_out": round(proceeds, 2), "note": "closed at end"})
        equity_values.append(cash)

    # max drawdown
    peak = equity_values[0] if equity_values else 0.0
    max_dd = 0.0
    for v in equity_values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        if dd > max_dd:
            max_dd = dd

    total_return = (equity_values[-1] / starting_cash - 1) * 100 if equity_values else 0.0

    # daily returns from the equity curve
    daily_returns = []
    for j in range(1, len(equity_values)):
        daily_returns.append(equity_values[j] / equity_values[j - 1] - 1)

    # sharpe, annualized with sqrt(365) since crypto trades daily
    if len(daily_returns) > 1:
        mean_r = sum(daily_returns) / len(daily_returns)
        var = sum((r - mean_r) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
        std_r = math.sqrt(var)
        sharpe = (mean_r / std_r) * math.sqrt(365) if std_r > 0 else 0.0
    else:
        sharpe = 0.0

    # cagr from calendar time between first and last candle
    if len(equity_values) > 1:
        start_ts = pd.Timestamp(df["timestamp"].iloc[warmup])
        end_ts = pd.Timestamp(df["timestamp"].iloc[len(df) - 1])
        years = (end_ts - start_ts).total_seconds() / (365.25 * 24 * 3600)
        cagr = ((equity_values[-1] / starting_cash) ** (1 / years) - 1) * 100 if years > 0 else 0.0
    else:
        cagr = 0.0

    # fraction of bars holding the asset
    total_bars = len(equity_values)
    exposure = bars_in_market / total_bars * 100 if total_bars > 0 else 0.0

    return {
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "cagr": cagr,
        "exposure": exposure,
        "trades": trades,
        "wins": wins,
        "sells": sells,
        "round_trips": round_trips,
        "final_equity": equity_values[-1] if equity_values else starting_cash,
    }
