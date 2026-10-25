"""Monte Carlo Simulation

Post: https://mathforfinance.com/monte-carlo-simulation/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np

def mc_call(S0, K, T, r, sigma, n_paths, seed=0):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    disc_payoff = np.exp(-r * T) * np.maximum(ST - K, 0)
    price = disc_payoff.mean()
    std_err = disc_payoff.std(ddof=1) / np.sqrt(n_paths)
    return price, std_err

# %% Snippet 2
def mc_asian(S0, K, T, r, sigma, n_steps, n_paths, seed=0):
    rng = np.random.default_rng(seed)
    dt = T / n_steps
    Z = rng.standard_normal((n_paths, n_steps))
    log_paths = np.cumsum((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z, axis=1)
    S = S0 * np.exp(log_paths)
    payoff = np.maximum(S.mean(axis=1) - K, 0)      # arithmetic average
    disc = np.exp(-r * T) * payoff
    return disc.mean(), disc.std(ddof=1) / np.sqrt(n_paths)

print(mc_asian(100, 100, 1, 0.05, 0.2, n_steps=252, n_paths=100_000))
# about 5.78, standard error about 0.025

# %% Snippet 3
L = np.linalg.cholesky(corr)
Z = rng.standard_normal((n_paths, n_assets)) @ L.T
