import numpy as np
import pandas as pd

def run_backtest(close, signal, open_ = None, initial_cash = 100000.0, fee_bps = 1.0, slippage_bps = 0.0, align_signal = False):
    signal = signal.copy()

    if align_signal:
        signal = signal.shift(1).fillna(0).astype(int)
    else:
        signal = signal.astype(int)
    
    trade_px_src = open_ if open_ is not None else close
    exec_px = trade_px_src.shift(-1)   # next bar
    slip_mult_buy  = 1.0 + slippage_bps/10_000.0
    slip_mult_sell = 1.0 - slippage_bps/10_000.0

    idx = close.index
    position   = np.zeros(len(idx), dtype=int)
    shares_arr = np.zeros(len(idx), dtype=float)
    trade_arr  = np.zeros(len(idx), dtype=float)
    exec_arr   = np.full(len(idx), np.nan, dtype=float)
    cash_arr   = np.zeros(len(idx), dtype=float)
    hold_arr   = np.zeros(len(idx), dtype=float)
    equity_arr = np.zeros(len(idx), dtype=float)
    fees_arr   = np.zeros(len(idx), dtype=float)

    cash = float(initial_cash)
    shares = 0.0
    last_position = 0

    for i, trade in enumerate(idx):
        current_position = int(signal.iloc[i])
        px_mtm = close.iloc[i]
        px_exec = exec_px.iloc[i]

        trade_shares = 0.0
        fees_today = 0.0

        # Enter or exit only if execution price exists (not last bar)
        if not np.isnan(px_exec) and current_position != last_position:
            if current_position == 1 and last_position == 0:
                # BUY max shares we can afford, accounting for fees and slippage
                trade_price = px_exec * slip_mult_buy
                # approximate shares we can buy; fees scale with notional
                # notional = shares * trade_price; fee = fee_bps/1e4 * notional
                # effective cost per share = trade_price * (1 + fee_bps/1e4)
                effective_cost_per_share = trade_price * (1 + fee_bps/10_000.0)
                trade_shares = cash / effective_cost_per_share
                notional = trade_shares * trade_price
                fees_today = (fee_bps/10_000.0) * notional
                cash -= (notional + fees_today)
                shares += trade_shares
                exec_arr[i] = trade_price
            elif current_position == 0 and last_position == 1:
                trade_price = px_exec * slip_mult_sell
                trade_shares = -shares
                notional = (-trade_shares) * trade_price  # positive notional
                fees_today = (fee_bps/10_000.0) * notional
                cash += (notional - fees_today)
                shares = 0.0
                exec_arr[i] = trade_price

        # mark-to-market
        holdings = shares * px_mtm
        equity = cash + holdings

        position[i] = current_position
        shares_arr[i] = shares
        trade_arr[i] = trade_shares
        cash_arr[i] = cash
        hold_arr[i] = holdings
        equity_arr[i] = equity
        fees_arr[i] = fees_today
        last_position = current_position

    output = pd.DataFrame({
        "position": position,
        "shares": shares_arr,
        "trade_shares": trade_arr,
        "exec_px": exec_arr,
        "cash": cash_arr,
        "holdings": hold_arr,
        "equity": equity_arr,
        "fees": fees_arr
    },
    index=idx
    )

    return output

