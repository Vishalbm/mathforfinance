"""PCA on the Yield Curve

Post: https://mathforfinance.com/pca-on-the-yield-curve/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
import pandas as pd

# yields: DataFrame of daily yields (in %), columns = maturities, e.g. 2y, 5y, 10y, 30y
changes = yields.diff().dropna() * 100          # daily changes in basis points
changes = changes - changes.mean()

cov = np.cov(changes.values, rowvar=False)
eigvals, eigvecs = np.linalg.eigh(cov)          # ascending order
order = eigvals.argsort()[::-1]
eigvals, eigvecs = eigvals[order], eigvecs[:, order]

explained = eigvals / eigvals.sum()
loadings = pd.DataFrame(eigvecs[:, :3], index=yields.columns,
                        columns=["level", "slope", "curvature"])
print(explained[:3])
print(loadings)
