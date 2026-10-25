"""Finite Difference Methods for PDEs

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
from scipy.linalg import solve_banded

def bs_crank_nicolson(S0, K, T, r, sigma, S_max=300.0, M=300, N=300, kind="call"):
    dS, dt = S_max / M, T / N
    S = np.linspace(0.0, S_max, M + 1)
    V = np.maximum(S - K, 0) if kind == "call" else np.maximum(K - S, 0)

    i = np.arange(1, M)                                  # interior nodes
    a = 0.25 * dt * (sigma**2 * i**2 - r * i)
    b = -0.5 * dt * (sigma**2 * i**2 + r)
    c = 0.25 * dt * (sigma**2 * i**2 + r * i)

    # left-hand matrix (I - A/2) in banded form
    ab = np.zeros((3, M - 1))
    ab[0, 1:] = -c[:-1]
    ab[1, :] = 1 - b
    ab[2, :-1] = -a[1:]

    for n in range(N):
        tau = (n + 1) * dt
        rhs = a * V[:-2] + (1 + b) * V[1:-1] + c * V[2:]  # (I + A/2) V
        if kind == "call":
            lo, hi = 0.0, S_max - K * np.exp(-r * tau)
        else:
            lo, hi = K * np.exp(-r * tau), 0.0
        rhs[0] += a[0] * lo
        rhs[-1] += c[-1] * hi
        V[1:-1] = solve_banded((1, 1), ab, rhs)
        V[0], V[-1] = lo, hi
    return np.interp(S0, S, V)
