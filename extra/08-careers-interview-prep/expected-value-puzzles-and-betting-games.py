"""Expected Value Puzzles and Betting Games

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
from functools import lru_cache

@lru_cache(maxsize=None)
def V(r, b):
    if r == 0:
        return 0.0
    if b == 0:
        return float(r)
    n = r + b
    keep_going = r / n * (1 + V(r - 1, b)) + b / n * (-1 + V(r, b - 1))
    return max(0.0, keep_going)

print(V(26, 26))   # about 2.62
