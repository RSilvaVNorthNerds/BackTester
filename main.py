from src.data import get_price_data
import pandas as pd
from src.indicators import simple_moving_average, zscore

# df = get_price_data(["AAPL", "MSFT"], "2020-03-02", "2020-03-03")

# print(df)

series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

output = simple_moving_average(series, 3)

z3 = zscore(series, 3)

flat = pd.Series([5] * 10)

z3_flat = zscore(flat, 4)

print(output.to_list())
print(z3.to_list())
print(z3_flat.to_list())