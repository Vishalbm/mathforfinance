"""Cointegration and Pairs Trading

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint

# y, x: pandas Series of log prices for the two stocks (training period)
score, pvalue, _ = coint(y, x)
beta = sm.OLS(y, sm.add_constant(x)).fit().params.iloc[1]

spread = y - beta * x
z = (spread - spread.mean()) / spread.std()

phi = sm.OLS(spread.diff().dropna(), sm.add_constant(spread.shift(1).dropna())).fit().params.iloc[1] + 1
half_life = np.log(0.5) / np.log(phi)
