import pandas as pd         
from src.data import get_price_data

def test_get_price_data():
    # Use a date range that includes actual trading days (avoid holidays/weekends)
    df = get_price_data(["AAPL", "MSFT"], "2020-03-02", "2020-03-03")
    assert isinstance(df.index, pd.DatetimeIndex)
    assert ("AAPL", "Close") in df.columns
    assert ("MSFT", "Close") in df.columns
    assert df.index.is_monotonic_increasing
    assert df.index.tz is None