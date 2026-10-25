"""Variance Reduction Tricks

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
Y_anti = 0.5 * (payoff(Z[: n // 2]) + payoff(-Z[: n // 2]))
price = Y_anti.mean()
std_err = Y_anti.std(ddof=1) / np.sqrt(n // 2)

# %% Snippet 2
X = disc * ST                                  # known mean: S0
b = np.cov(Y, X)[0, 1] / X.var(ddof=1)
Y_cv = Y - b * (X - S0)
price = Y_cv.mean()
std_err = Y_cv.std(ddof=1) / np.sqrt(n)

# %% Snippet 3
from scipy.stats import qmc, norm

sampler = qmc.Sobol(d=1, scramble=True, seed=0)
U = sampler.random(2**16)                  # Sobol points in [0, 1)
Z_qmc = norm.ppf(U).ravel()                # transform to normals
