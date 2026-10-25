"""Calibrating Models to Market Data

Post: https://mathforfinance.com/calibrating-models-to-market-data/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
from scipy.optimize import least_squares

S0, T, r = 100, 1.0, 0.05
strikes = np.array([80, 90, 100, 110, 120])
true = dict(v0=0.04, kappa=2.0, theta=0.04, xi=0.5, rho=-0.7)
market = np.array([call_price(lambda u: heston_cf(u, S0, T, r, **true), S0, K, T, r)
                   for K in strikes])

def residuals(p):
    v0, kappa, theta, xi, rho = p
    cf = lambda u: heston_cf(u, S0, T, r, v0, kappa, theta, xi, rho)
    return np.array([call_price(cf, S0, K, T, r) for K in strikes]) - market

x0 = [0.06, 1.0, 0.06, 0.3, -0.3]                       # deliberately poor start
bounds = ([1e-4, 0.01, 1e-4, 0.01, -0.99], [1.0, 10.0, 1.0, 2.0, 0.99])
fit = least_squares(residuals, x0, bounds=bounds)
print(np.round(fit.x, 4))      # [ 0.04  2.    0.04  0.5  -0.7 ]
