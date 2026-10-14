# run the backtest

from config import FAST, SLOW, FEE, SLIPPAGE_BPS, STARTING_CASH
from data import load_candles
from engine import run_backtest


def main():
    df = load_candles()
    results = run_backtest(df, FAST, SLOW, FEE, SLIPPAGE_BPS, STARTING_CASH)

    print("")
    print("===== RESULTS =====")
    print("total return:", round(results["total_return"], 2), "%")
    print("cagr:", round(results["cagr"], 2), "%")
    print("max drawdown:", round(results["max_drawdown"] * 100, 2), "%")
    print("sharpe:", round(results["sharpe"], 2))
    print("exposure:", round(results["exposure"], 1), "%")
    print("round trips:", results["round_trips"])
    if results["sells"] > 0:
        print("win rate:", round(results["wins"] / results["sells"] * 100, 1), "% (of", results["sells"], "closed trades)")
    print("final equity: $", round(results["final_equity"], 2))

    print("")
    print("trade log:")
    for t in results["trades"]:
        print(t)


main()
