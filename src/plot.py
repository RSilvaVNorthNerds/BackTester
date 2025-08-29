import matplotlib.pyplot as plt
from src.metrics import drawdown_series

def plot_equity(equity, title="Equity Curve"):
    plt.figure(figsize=(10,4))
    plt.plot(equity.index, equity.values, label="Equity")
    plt.title(title)
    plt.ylabel("Equity ($)")
    plt.xlabel("Date")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

def plot_drawdown(equity, title="Drawdown"):
    dd = drawdown_series(equity)
    plt.figure(figsize=(10,3))
    plt.fill_between(dd.index, dd.values, 0, color="red", alpha=0.3)
    plt.title(title)
    plt.ylabel("Drawdown (%)")
    plt.xlabel("Date")
    plt.show()

def plot_signals(close, signal, title="Price + Signals"):
    plt.figure(figsize=(10,4))
    plt.plot(close.index, close.values, label="Close")
    buy_dates = close.index[(signal.diff() > 0)]
    sell_dates = close.index[(signal.diff() < 0)]
    plt.scatter(buy_dates, close.loc[buy_dates], marker="^", color="green", label="Buy")
    plt.scatter(sell_dates, close.loc[sell_dates], marker="v", color="red", label="Sell")
    plt.title(title)
    plt.legend()
    plt.show()