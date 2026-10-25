"""Fast Code: Vectorization and C++ for Quants

Post: https://mathforfinance.com/fast-code-vectorization-and-c-for-quants/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import cProfile, pstats

cProfile.run("run_backtest()", "profile.out")
pstats.Stats("profile.out").sort_stats("cumulative").print_stats(15)

# %% Snippet 2
import math, random
import numpy as np

def mc_loop(S0, K, T, r, sigma, n):
    total = 0.0
    for _ in range(n):
        z = random.gauss(0.0, 1.0)
        ST = S0 * math.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * z)
        total += max(ST - K, 0.0)
    return math.exp(-r * T) * total / n

def mc_numpy(S0, K, T, r, sigma, n):
    z = np.random.default_rng(0).standard_normal(n)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    return np.exp(-r * T) * np.maximum(ST - K, 0.0).mean()

# %% Snippet 3
import math
import numpy as np
from numba import njit

@njit(cache=True)
def mc_numba(S0, K, T, r, sigma, n, seed):
    np.random.seed(seed)
    drift = (r - 0.5 * sigma**2) * T
    vol = sigma * math.sqrt(T)
    total = 0.0
    for _ in range(n):
        ST = S0 * math.exp(drift + vol * np.random.standard_normal())
        if ST > K:
            total += ST - K
    return math.exp(-r * T) * total / n
