"""Risk Parity

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
from scipy.optimize import minimize

def erc_weights(cov):
    n = cov.shape[0]
    def objective(w):
        port_var = w @ cov @ w
        rc = w * (cov @ w) / port_var          # risk shares
        return ((rc - 1.0 / n) ** 2).sum()
    w0 = np.ones(n) / n
    cons = {"type": "eq", "fun": lambda w: w.sum() - 1}
    res = minimize(objective, w0, bounds=[(0, 1)] * n, constraints=cons)
    return res.x
