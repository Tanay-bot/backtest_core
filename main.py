# run the backtest

from config import FAST, SLOW, FEE, STARTING_CASH
from data import load_candles
from engine import run_backtest


def main():
    df = load_candles()
    results = run_backtest(df, FAST, SLOW, FEE, STARTING_CASH)

    print("")
    print("===== RESULTS =====")
    print("total return:", round(results["total_return"], 2), "%")
    print("max drawdown:", round(results["max_drawdown"] * 100, 2), "%")
    print("trades:", len(results["trades"]))
    if results["sells"] > 0:
        print("win rate:", round(results["wins"] / results["sells"] * 100, 1), "% (of", results["sells"], "sells)")
    print("final equity: $", round(results["final_equity"], 2))

    print("")
    print("trade log:")
    for t in results["trades"]:
        print(t)


main()
