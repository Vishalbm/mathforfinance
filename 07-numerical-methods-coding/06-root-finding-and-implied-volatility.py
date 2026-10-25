"""Root Finding and Implied Volatility

Post: https://mathforfinance.com/root-finding-and-implied-volatility/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
from scipy.stats import norm

def bs_call(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def bs_vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T)

def implied_vol_newton(price, S, K, T, r, sigma=0.2, tol=1e-10, max_iter=50):
    for _ in range(max_iter):
        diff = bs_call(S, K, T, r, sigma) - price
        if abs(diff) < tol:
            return sigma
        sigma -= diff / bs_vega(S, K, T, r, sigma)
    raise RuntimeError("Newton did not converge")

# %% Snippet 2
from scipy.optimize import brentq

sigma = brentq(lambda s: bs_call(100, 100, 1, 0.05, s) - 12.0, 1e-6, 5.0)
