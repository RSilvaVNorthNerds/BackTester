import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

def equity_to_retruns(equity: pd.Series) -> pd.Series:
    returns = equity.astype(float).pct_change()

    return returns.dropna()

def annualized_volume(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    
    return float(returns.std(ddof=0) * np.sqrt(TRADING_DAYS_PER_YEAR))

def sharpe(returns:pd.Series, risk_free_daily: float = 0.0) -> float:
    if returns.empty:
        return 0.0
    excess_returns = returns - risk_free_daily
    volume = excess_returns.std(ddof=0)

    if volume == 0 or np.isnan(volume):
        return 0.0
    
    mean = excess_returns.mean()

    return float((mean * TRADING_DAYS_PER_YEAR)/ (volume * np.sqrt(TRADING_DAYS_PER_YEAR)))

def sortino(returns: pd.Series, risk_free_daily: float = 0.0) -> float:
    if returns.empty:
        return 0.0
    excess_returns = returns - risk_free_daily
    downside_returns = excess_returns[excess_returns < 0]
    
    downside_vol = downside_returns.std(ddof=0)

    if downside_vol == 0 or np.isnan(downside_vol):
        return 0.0
    
    mean = excess_returns.mean()

    return float((mean * TRADING_DAYS_PER_YEAR)/ (downside_vol * np.sqrt(TRADING_DAYS_PER_YEAR)))


def compound_annual_growth_rate(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    
    start = float(equity.iloc[0])
    end = float(equity.iloc[-1])

    if start <= 0:
        return 0.0
    
    n_days = max((equity.index[-1] - equity.index[0]).days, 1)
    years = n_days / 365.25

    return float((end/start) ** (1/years) - 1) if years > 0 else 0.0

def drawdown_series(equity: pd.Series) -> pd.Series:
    if equity.empty:
        return pd.Series(dtype=float)
    
    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1.0

    return drawdown

def max_drawdown(equity: pd.Series) -> float:
    drawdown = drawdown_series(equity)

    return float(drawdown.min()) if not drawdown.empty else 0.0

def longest_drawdown_days(equity: pd.Series) -> int:
    if equity.empty:
        return 0
    
    drawdown = drawdown_series(equity)
    in_drawdown = drawdown < 0
    longest = current = 0
    prev = False

    for flag in in_drawdown:
        if flag:
            current = current + 1 if prev else 1
            prev = True
        else:
            longest = max(longest, current)
            current = 0
            prev = False
    longest = max(longest, current)

    return int(longest)

def extract_trades(bt: pd.DataFrame) -> pd.DataFrame:
    """
    From backtest output (with columns: trade_shares, exec_px),
    build a trade ledger: each BUY matched to the next SELL.
    Assumes long/flat (no shorts), all-in/all-out.
    """
    trades = []
    entry_price = None
    entry_date = None
    entry_shares = None

    for dt, row in bt.iterrows():
        ts = row.get("trade_shares", 0.0)
        px = row.get("exec_px", np.nan)
        if np.isnan(px) or ts == 0:
            continue
        if ts > 0 and entry_price is None:
            # entry
            entry_price = float(px)
            entry_date = dt
            entry_shares = float(ts)
        elif ts < 0 and entry_price is not None:
            # exit
            exit_price = float(px)
            exit_date = dt
            shares = entry_shares  # positive
            pnl = (exit_price - entry_price) * shares
            ret = (exit_price / entry_price) - 1.0
            trades.append({
                "entry_date": entry_date, "entry_px": entry_price,
                "exit_date": exit_date,   "exit_px": exit_price,
                "shares": shares, "pnl": pnl, "return": ret
            })
            entry_price = entry_date = entry_shares = None

    return pd.DataFrame(trades)

def trade_stats(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"num_trades": 0, "win_rate": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "profit_factor": 0.0}
    
    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] < 0]
    total_win = float(wins["pnl"].sum()) if not wins.empty else 0.0
    total_loss = -float(losses["pnl"].sum()) if not losses.empty else 0.0  
    profit_factor = (total_win / total_loss) if total_loss > 0 else np.inf if total_win > 0 else 0.0

    return {
        "num_trades": int(len(trades)),
        "win_rate": float(len(wins) / len(trades)),
        "avg_win": float(wins["pnl"].mean()) if not wins.empty else 0.0,
        "avg_loss": float(losses["pnl"].mean()) if not losses.empty else 0.0,
        "profit_factor": float(profit_factor),
    }

def summarize_backtest_performance(equity: pd.Series, rf_daily: float = 0.0) -> dict:
    """One call to get all the metrics"""
    returns = equity_to_retruns(equity)

    return {
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1.0) if len(equity) >= 2 else 0.0,
        "CAGR": compound_annual_growth_rate(equity),
        "vol_ann": annualized_volume(returns),
        "sharpe": sharpe(returns, rf_daily),
        "sortino": sortino(returns, rf_daily),
        "max_drawdown": max_drawdown(equity),
        "longest_drawdown_days": longest_drawdown_days(equity),
    }
    