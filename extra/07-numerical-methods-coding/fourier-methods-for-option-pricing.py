"""Fourier Methods for Option Pricing

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import numpy as np
from scipy.integrate import quad

def heston_cf(u, S0, T, r, v0, kappa, theta, xi, rho):
    """Characteristic function of ln S_T under Heston (stable formulation)."""
    d = np.sqrt((rho * xi * 1j * u - kappa)**2 + xi**2 * (1j * u + u**2))
    g = (kappa - rho * xi * 1j * u - d) / (kappa - rho * xi * 1j * u + d)
    C = (kappa * theta / xi**2) * ((kappa - rho * xi * 1j * u - d) * T
         - 2 * np.log((1 - g * np.exp(-d * T)) / (1 - g)))
    D = ((kappa - rho * xi * 1j * u - d) / xi**2) * (1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T))
    return np.exp(1j * u * (np.log(S0) + r * T) + C + D * v0)

def call_price(cf, S0, K, T, r):
    k = np.log(K)
    p2 = lambda u: (np.exp(-1j * u * k) * cf(u) / (1j * u)).real
    p1 = lambda u: (np.exp(-1j * u * k) * cf(u - 1j) / (1j * u * cf(-1j))).real
    P1 = 0.5 + quad(p1, 1e-8, 200, limit=200)[0] / np.pi
    P2 = 0.5 + quad(p2, 1e-8, 200, limit=200)[0] / np.pi
    return S0 * P1 - K * np.exp(-r * T) * P2
