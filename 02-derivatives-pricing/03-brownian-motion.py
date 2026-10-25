"""Brownian Motion

Post: https://mathforfinance.com/brownian-motion/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np

T, n_steps, n_paths = 1.0, 252, 5
dt = T / n_steps
rng = np.random.default_rng(0)

# Brownian increments: N(0, dt)
dW = rng.normal(0.0, np.sqrt(dt), size=(n_paths, n_steps))
W = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1)

# geometric Brownian motion, simulated exactly
S0, mu, sigma = 100.0, 0.08, 0.20
t = np.linspace(0.0, T, n_steps + 1)
S = S0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * W)

# quadratic variation check: should be close to T = 1
print((dW**2).sum(axis=1))
