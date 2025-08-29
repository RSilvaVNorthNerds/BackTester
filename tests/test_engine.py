from src.data import get_price_data
from src.strategies import signal_sma_crossover, align_next_bar
from src.engine import run_backtest

def test_engine():
    """Test the backtesting engine with SMA crossover strategy"""
    df = get_price_data(["AAPL"], "2022-01-01", "2022-06-30")
    close = df[("AAPL","Close")]
    open_ = df[("AAPL","Open")] if ("AAPL","Open") in df.columns else None

    sig_raw = signal_sma_crossover(close, fast=10, slow=30)
    sig = align_next_bar(sig_raw)

    bt = run_backtest(close, sig, open_=open_, initial_cash=100_000, fee_bps=1, slippage_bps=0)

    # Basic invariants
    assert not bt["equity"].isna().any()
    assert bt.index.equals(close.index)
    
    # Additional test assertions
    assert len(bt) > 0, "Backtest result should not be empty"
    assert "equity" in bt.columns, "Backtest should have equity column"
    assert bt["equity"].iloc[-1] > 0, "Final equity should be positive"
