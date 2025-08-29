import pandas as pd
from indicators import simple_moving_average, zscore

def signal_sma_crossover(close, fast, slow) -> pd.Series:
    fast_sma = simple_moving_average(close, fast)
    slow_sma = simple_moving_average(close, slow)

    cross_above = fast_sma > slow_sma and fast_sma.shift(1) <= slow_sma.shift(1)
    cross_below = fast_sma < slow_sma and fast_sma.shift(1) >= slow_sma.shift(1)

    positions = []
    current = 0

    for up, down in zip(cross_above.fillna(False), cross_below.fillna(False)):
        if up:
            current = 1
        elif down:
            current = 0
        positions.append(current)

    signal = pd.Series(positions, index=close.index, dtype="int64")

    warmup = max(fast, slow) - 1
    signal.iloc[:warmup] = 0

    return signal

def signal_mean_reversion(close, lookback, entry, exit) -> pd.Series:
    z_score_output = zscore(close, lookback)
    enter_long = z_score_output <= -entry

    exit_flat = z_score_output.abs() <= exit

    positions = []
    current = 0

    for enter, exit in zip(enter_long.fillna(False), exit_flat.fillna(False)):
        if current == 0 and enter:
            current = 1
        elif current == 1 and exit:
            current = 0
        positions.append(current)

    signal = pd.Series(positions, index=close.index, dtype="int64")
    signal.iloc[:lookback - 1] = 0

    return signal

def align_next_bar(signal:pd.Series) -> pd.Series:
    return signal.shift(1).fillna(0).astype("int64")