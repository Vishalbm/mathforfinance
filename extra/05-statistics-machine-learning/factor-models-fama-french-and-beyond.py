"""Factor Models: Fama–French and Beyond

Post not currently published on the site.

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import statsmodels.api as sm

# df has columns: fund_excess, MKT, SMB, HML, MOM (monthly, in percent)
X = sm.add_constant(df[["MKT", "SMB", "HML", "MOM"]])
result = sm.OLS(df["fund_excess"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
print(result.params)   # alpha (const) and factor loadings
print(result.tvalues)
