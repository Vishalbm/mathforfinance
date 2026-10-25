"""Coding Interviews for Quants

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
def max_profit(prices):
    """Best profit from one buy followed by one sell, in O(n)."""
    best, low = 0.0, float("inf")
    for p in prices:
        low = min(low, p)
        best = max(best, p - low)
    return best

max_profit([7, 1, 5, 3, 6, 4])   # 5: buy at 1, sell at 6

# %% Snippet 2
from collections import deque

def moving_average(stream, window):
    buf, total = deque(), 0.0
    for x in stream:
        buf.append(x)
        total += x
        if len(buf) > window:
            total -= buf.popleft()
        yield total / len(buf)

list(moving_average([1, 2, 3, 4, 5], 3))   # [1.0, 1.5, 2.0, 3.0, 4.0]

# %% Snippet 3
class RunningStats:
    def __init__(self):
        self.n, self.mean, self.m2 = 0, 0.0, 0.0

    def update(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)

    @property
    def variance(self):          # sample variance
        return self.m2 / (self.n - 1) if self.n > 1 else 0.0

# %% Snippet 4
import random

def reservoir_sample(stream, k, rng=random):
    sample = []
    for i, x in enumerate(stream):
        if i < k:
            sample.append(x)
        else:
            j = rng.randint(0, i)      # inclusive on both ends
            if j < k:
                sample[j] = x
    return sample
