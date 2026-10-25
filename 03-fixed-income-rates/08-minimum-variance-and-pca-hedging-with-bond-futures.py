"""Minimum-Variance and PCA Hedging with Bond Futures

Post: https://mathforfinance.com/minimum-variance-and-pca-hedging-with-bond-futures/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np

vol = np.array([4.5, 5.5, 5.8, 5.6])                      # daily bp vol: 2y, 5y, 10y, 30y
corr = np.array([[1.00, 0.85, 0.70, 0.55],
                 [0.85, 1.00, 0.90, 0.75],
                 [0.70, 0.90, 1.00, 0.90],
                 [0.55, 0.75, 0.90, 1.00]])
S = np.outer(vol, vol) * corr
x = np.array([3_000, 12_000, 25_000, 6_000.0])           # portfolio KR DV01 (EUR/bp)
B = np.zeros((4, 2)); B[1, 0] = 45; B[2, 1] = 82          # Bobl, Bund DV01 per contract

n_mv = np.linalg.solve(B.T @ S @ B, B.T @ S @ x)          # minimum-variance hedge

w, V = np.linalg.eigh(S); V = V[:, np.argsort(w)[::-1]]
n_pca = np.linalg.solve(V[:, :2].T @ B, V[:, :2].T @ x)   # level + slope neutral

residual = lambda n: np.sqrt((x - B @ n) @ S @ (x - B @ n))
print(n_mv.round(), residual(n_mv).round(), n_pca.round(), residual(n_pca).round())
