"""Linear Algebra for Portfolios

Post: https://mathforfinance.com/linear-algebra-for-portfolios/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np

vol = np.array([0.20, 0.15, 0.10])
corr = np.array([[1.0, 0.5, 0.2],
                 [0.5, 1.0, 0.3],
                 [0.2, 0.3, 1.0]])
cov = np.outer(vol, vol) * corr          # Sigma = D R D
w = np.array([0.5, 0.3, 0.2])

port_vol = np.sqrt(w @ cov @ w)          # 0.1351
risk_contrib = w * (cov @ w) / port_vol  # adds up to port_vol
eigvals = np.linalg.eigvalsh(cov)        # all should be >= 0
