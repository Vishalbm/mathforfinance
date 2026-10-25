"""Pricing Options with a Binomial Tree in Python

Post: https://mathforfinance.com/pricing-options-with-a-binomial-tree-in-python/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np

def binomial_price(S0, K, T, r, sigma, n, kind="call", american=False):
    """Cox-Ross-Rubinstein binomial tree price."""
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    q = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    # stock prices at maturity: S0 * u^j * d^(n-j), j = 0..n
    j = np.arange(n + 1)
    S = S0 * u**j * d**(n - j)
    V = np.maximum(S - K, 0) if kind == "call" else np.maximum(K - S, 0)

    # backward induction, one time step at a time
    for step in range(n - 1, -1, -1):
        V = disc * (q * V[1:] + (1 - q) * V[:-1])
        if american:
            k = np.arange(step + 1)
            S = S0 * u**k * d**(step - k)
            exercise = np.maximum(S - K, 0) if kind == "call" else np.maximum(K - S, 0)
            V = np.maximum(V, exercise)
    return V[0]

# %% Snippet 2
for n in [10, 100, 1000]:
    print(n,
          round(binomial_price(100, 100, 1, 0.05, 0.2, n), 4),
          round(binomial_price(100, 100, 1, 0.05, 0.2, n, "put"), 4),
          round(binomial_price(100, 100, 1, 0.05, 0.2, n, "put", american=True), 4))
