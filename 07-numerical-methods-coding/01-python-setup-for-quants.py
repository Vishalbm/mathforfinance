"""Python Setup for Quants

Post: https://mathforfinance.com/python-setup-for-quants/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
# Run in a terminal (not Python):
# create a project folder and a virtual environment inside it
# mkdir quant && cd quant
# python -m venv .venv
# 
# activate it (macOS / Linux)
# source .venv/bin/activate
# on Windows: .venv\Scripts\activate

# %% Snippet 2
# Run in a terminal (not Python):
# pip install numpy pandas scipy matplotlib jupyterlab statsmodels yfinance

# %% Snippet 3
# Run in a terminal (not Python):
# jupyter lab

# %% Snippet 4
import numpy as np
import pandas as pd

# simulate one year of daily log returns: mean 0.04%, volatility 1.2% a day
rng = np.random.default_rng(42)
n_days = 252
daily_log_returns = rng.normal(0.0004, 0.012, n_days)

# turn returns into a price path starting at 100
prices = 100 * np.exp(np.cumsum(daily_log_returns))
dates = pd.bdate_range("2025-01-02", periods=n_days)
px = pd.Series(prices, index=dates, name="price")

# log returns from prices, then annualize
rets = np.log(px / px.shift(1)).dropna()
print(f"Annualized volatility: {rets.std() * np.sqrt(252):.1%}")
print(f"Total return: {px.iloc[-1] / px.iloc[0] - 1:.1%}")

px.plot(title="Simulated price path")

# %% Snippet 5
import yfinance as yf

px = yf.download("SPY", start="2020-01-01", auto_adjust=True)["Close"].squeeze()

# %% Snippet 6
import numpy as np
from scipy.stats import norm

def bs_call(S, K, T, r, sigma):
    """Black-Scholes price of a European call option."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

print(round(bs_call(S=100, K=100, T=1.0, r=0.05, sigma=0.20), 2))  # 10.45
