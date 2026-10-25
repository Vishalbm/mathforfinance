"""Getting and Cleaning Market Data

Post: https://mathforfinance.com/getting-and-cleaning-market-data/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
import pandas as pd
import yfinance as yf

tickers = ["SPY", "TLT", "GLD"]
raw = yf.download(tickers, start="2010-01-01", auto_adjust=True, progress=False)
px = raw["Close"]

# 1. Inspect
print(px.describe())
print(px.isna().sum())

# 2. Align to a common calendar and handle gaps
px = px.dropna(how="all")             # drop days where nothing traded
px = px.ffill(limit=3)                # carry forward short gaps only

# 3. Compute returns
rets = np.log(px / px.shift(1)).dropna()

# 4. Flag suspicious moves: more than 8 rolling standard deviations
vol = rets.rolling(60, min_periods=20).std()
flags = (rets.abs() > 8 * vol.shift(1))
print(rets[flags.any(axis=1)])

# 5. Save a clean copy
rets.to_parquet("returns_clean.parquet")
