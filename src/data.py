import yfinance as yf
import pandas as pd
import os


def _clean_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df = df.tz_localize(None)
    return df.sort_index().loc[~df.index.duplicated(keep="last")]

"""
This function downloads price data for a list of tickers from Yahoo Finance and caches it in a local directory.

Parameters:
tickers: list[str] - The list of tickers to download data for.
start_date: str - The start date for the data.
end_date: str - The end date for the data.
cache_dir: str - The directory to cache the data in.
"""
def get_price_data(tickers: list[str], start_date: str, end_date: str, cache_dir: str = "data/") -> pd.DataFrame:
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False, group_by="ticker")

    os.makedirs(cache_dir, exist_ok=True)

    all_data = []

    for ticker in tickers:    
        if isinstance(data.columns, pd.MultiIndex):
            if ticker not in data.columns.get_level_values(0):
                raise ValueError(f"Ticker {ticker} not found in downloaded data.")
            ticker_data = data[ticker]
        else:
            # single-ticker request - raw already has columns like 'Open','Close',...
            ticker_data = data.copy()  
  
        ticker_data = _clean_index(ticker_data)


        cache_file = f"{cache_dir}/{ticker}.csv"
        if os.path.exists(cache_file):
            cached = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            cached = _clean_index(cached)
            # Merge & prefer latest from freshly downloaded
            merged = pd.concat([cached, ticker_data], axis=0)
            merged = _clean_index(merged)
            # Trim to requested range if you want strict range:
            merged = merged.loc[(merged.index >= pd.to_datetime(start_date)) & (merged.index <= pd.to_datetime(end_date))]
            merged.to_csv(cache_file)
            ticker_data = merged
        else:
            ticker_data.to_csv(cache_file)
        
        ticker_data.columns = pd.MultiIndex.from_product([[ticker], ticker_data.columns])
        all_data.append(ticker_data)

    combined_df = pd.concat(all_data, axis=1, join="outer")

    return combined_df
        








