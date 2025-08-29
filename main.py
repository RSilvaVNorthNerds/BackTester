from src.data import get_price_data
from src.strategies import signal_sma_crossover, align_next_bar
from src.engine import run_backtest
import pandas as pd

"""
Quick test of the backtest engine + signals with real data
"""

# --- get 1 year of AAPL + MSFT ---
df = get_price_data(["AAPL","MSFT"], "2022-01-01", "2022-12-31")
aapl_close = df[("AAPL","Close")]
msft_close = df[("MSFT","Close")]

# --- strategy: 20/50 SMA crossover ---
sig_aapl_raw = signal_sma_crossover(aapl_close, fast=20, slow=50)
sig_msft_raw = signal_sma_crossover(msft_close, fast=20, slow=50)

sig_aapl = align_next_bar(sig_aapl_raw)
sig_msft = align_next_bar(sig_msft_raw)

# --- run backtests ---
bt_aapl = run_backtest(aapl_close, sig_aapl, initial_cash=100_000, fee_bps=1)
bt_msft = run_backtest(msft_close, sig_msft, initial_cash=100_000, fee_bps=1)

print("AAPL final equity:", bt_aapl["equity"].iloc[-1])
print("MSFT final equity:", bt_msft["equity"].iloc[-1])

print("\nAAPL sample:")
print(bt_aapl.head(3))
print(bt_aapl.tail(3))

print("\nMSFT sample:")
print(bt_msft.head(3))
print(bt_msft.tail(3))