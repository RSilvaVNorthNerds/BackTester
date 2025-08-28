import pandas as pd
import numpy as np

def simple_moving_average(series, window) -> pd.Series:
    if window < 1:
        raise ValueError("Window must be at least 1")
    
    s = pd.Series(series, dtype="float64")
    
    return s.rolling(window=window, min_periods=window).mean()

    


def zscore(series, lookback):
    if lookback < 1:
        raise ValueError("Lookback must be at least 1")
    
    s = pd.Series(series, dtype="float64")

    mean = s.rolling(window=lookback, min_periods=lookback).mean()
    std = s.rolling(window=lookback, min_periods=lookback).std(ddof=0)

    z_score = (s - mean) / std

    z_score = z_score.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    z_score.iloc[: lookback - 1] = np.nan

    return z_score