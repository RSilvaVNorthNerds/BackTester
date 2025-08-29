from src.data import get_price_data
from src.strategies import signal_sma_crossover, align_next_bar
from src.engine import run_backtest
import pandas as pd

"""
Quick test of the backtest engine
"""

# --- toy price data (7 days) ---
dates = pd.date_range("2022-01-03", periods=7, freq="B")  # business days
close = pd.Series([100, 101, 102, 103, 104, 105, 106], index=dates, name="Close")

# --- toy signal ---
# 0 = flat, 1 = long
# Go long on day 2, stay long until day 5, then flat again
signal = pd.Series([0, 1, 1, 1, 0, 0, 0], index=dates, name="Signal")

# --- run backtest ---
bt = run_backtest(close, signal, initial_cash=1000, fee_bps=0, slippage_bps=0, align_signal=False)

print(close)
print(signal)
print(bt)
print("Final equity:", bt["equity"].iloc[-1])