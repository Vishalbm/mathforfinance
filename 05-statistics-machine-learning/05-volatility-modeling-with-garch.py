"""Volatility Modeling with GARCH

Post: https://mathforfinance.com/volatility-modeling-with-garch/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
from arch import arch_model

# returns: a pandas Series of daily returns, in percent
model = arch_model(returns, mean="Constant", vol="GARCH", p=1, q=1, dist="t")
result = model.fit(disp="off")
print(result.summary())

# variance forecasts for the next 20 days
forecast = result.forecast(horizon=20)
print(forecast.variance.iloc[-1] ** 0.5)  # daily volatility forecasts
