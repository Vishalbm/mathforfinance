"""Classification Models for Execution Signals

Post: https://mathforfinance.com/classification-models-for-execution-signals/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss

# X: features (imbalance, momentum, spread, ...), y: next move up (1) or down (0)
# rows sorted by time; never shuffle across time
split = int(0.7 * len(X))
model = LogisticRegression(C=1.0).fit(X[:split], y[:split])
p = model.predict_proba(X[split:])[:, 1]

print(roc_auc_score(y[split:], p), brier_score_loss(y[split:], p), log_loss(y[split:], p))
