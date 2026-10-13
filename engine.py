# sma crossover backtest engine

# run the backtest, returns dict with results and trade log
def run_backtest(df, fast, slow, fee, starting_cash):
    df["sma_fast"] = df["close"].rolling(fast).mean()
    df["sma_slow"] = df["close"].rolling(slow).mean()

    cash = starting_cash
    coins = 0.0
    last_buy_price = 0.0
    last_buy_cost = 0.0
    wins = 0
    sells = 0
    round_trips = 0

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

        open_price = df["open"].iloc[i]

        if target == 1 and coins == 0:
            coins = (cash * (1 - fee)) / open_price
            last_buy_price = open_price
            last_buy_cost = cash  # cash spent at entry, fees included
            trades.append({"date": df["timestamp"].iloc[i], "side": "BUY", "price": round(open_price, 2), "coins": round(coins, 6)})
            cash = 0.0
        elif target == 0 and coins > 0:
            proceeds = coins * open_price * (1 - fee)
            if proceeds > last_buy_cost:
                wins = wins + 1
            sells = sells + 1
            round_trips = round_trips + 1
            trades.append({"date": df["timestamp"].iloc[i], "side": "SELL", "price": round(open_price, 2), "cash_out": round(proceeds, 2)})
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

    return {
        "total_return": total_return,
        "max_drawdown": max_dd,
        "trades": trades,
        "wins": wins,
        "sells": sells,
        "round_trips": round_trips,
        "final_equity": equity_values[-1] if equity_values else starting_cash,
    }
