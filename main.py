from src.data import get_price_data

df = get_price_data(["AAPL", "MSFT"], "2020-03-02", "2020-03-03")

print(df)