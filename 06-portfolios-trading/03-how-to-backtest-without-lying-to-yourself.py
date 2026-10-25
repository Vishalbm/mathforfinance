"""How to Backtest Without Lying to Yourself

Post: https://mathforfinance.com/how-to-backtest-without-lying-to-yourself/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
# signal computed from data up to the close of day t
signal = compute_signal(prices)            # indexed by date t
position = signal.shift(1)                 # traded on day t+1
strategy_ret = position * returns          # returns earned on day t+1
