"""Momentum and Mean-Reversion Strategies

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import pandas as pd

# prices: DataFrame of month-end prices, columns = stocks
monthly_ret = prices.pct_change()

# 12-1 momentum: return from t-12 to t-1, skipping the latest month
mom = prices.shift(1) / prices.shift(12) - 1

# rank into deciles each month and form a long-short portfolio
ranks = mom.rank(axis=1, pct=True)
long = (ranks >= 0.9).astype(float)
short = (ranks <= 0.1).astype(float)
weights = long.div(long.sum(axis=1), axis=0) - short.div(short.sum(axis=1), axis=0)

# next-month return of the strategy (weights set at t, returns earned at t+1)
strategy_ret = (weights.shift(1) * monthly_ret).sum(axis=1)
