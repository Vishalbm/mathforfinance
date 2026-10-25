"""Machine Learning for Return Prediction

Post: https://mathforfinance.com/machine-learning-for-return-prediction/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit

# X: features, y: next-period returns, both sorted by date
tscv = TimeSeriesSplit(n_splits=5, gap=21)   # gap ~ one month to limit leakage
scores = []
for train_idx, test_idx in tscv.split(X):
    model = Ridge(alpha=10.0).fit(X.iloc[train_idx], y.iloc[train_idx])
    scores.append(model.score(X.iloc[test_idx], y.iloc[test_idx]))
print(scores)  # out-of-sample R^2 per fold
