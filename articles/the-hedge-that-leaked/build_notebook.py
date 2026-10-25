import nbformat as nbf
nb = nbf.v4.new_notebook()
M, C = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
M("""# The Hedge That Leaked: notebook

Companion to the article on [mathforfinance.com](https://mathforfinance.com). Every number and chart in the article is produced here from the raw files in `data/raw/` (repo root).

**Question:** a trader is long \\$100mm of the on-the-run 10-year Treasury note and hedges by selling Treasury futures. How well does each hedge hold up when the curve twists, as it did around the failure of Silicon Valley Bank (10–13 March 2023)?

Hedges compared (rebalanced daily, using only information available that day):
1. DV01 match with TY, CME's "10-Year" contract, whose cheapest-to-deliver is a ~7-year note
2. DV01 match with UXY, the Ultra 10-Year (CME code TN), whose cheapest-to-deliver is a ~10-year note
3. Key-rate hedge with FV, TY and UXY, matching risk in 1-5y, 7y and 10-30y buckets (Ho, 1992)
4. PCA hedge neutralising level and slope with FV and UXY (Litterman and Scheinkman, 1991)

Run order: `src/validate_cf.py` → `src/experiment.py` → `src/figures.py` → `src/validation.py`. The cells below do exactly that."""),
C("""import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path('src').resolve()))
import pandas as pd, numpy as np
from IPython.display import Image, display
pd.set_option('display.width', 160); pd.set_option('display.max_columns', 20)
ART = pathlib.Path("src").resolve().parent; SRC = str(ART/"src")
import mff_rates   # moves the working directory to the repo root
print('working dir:', pathlib.Path.cwd())"""),
M("## 1. Raw data snapshot\nWhat each file is and where it came from is listed in `data/README.md`."),
C("""for f in sorted(pathlib.Path('data/raw').iterdir()):
    print(f'{f.name:70s} {f.stat().st_size/1e3:8.1f} kB')"""),
M("## 2. Check the conversion-factor formula against CME's published table\nCME publishes conversion factors for every deliverable note and bond for currently listed contracts. If our formula is right, every one should match to 4 decimals."),
C("%run {SRC}/validate_cf.py"),
M("## 3. Run the hedge experiment (Q1 2023, daily)\nFits a Svensson curve to FedInvest prices each day, values FV/TY/UXY futures from the cheapest-to-deliver forward price, computes key-rate risk, PCA loadings (250 days of par-yield changes up to that day), hedge ratios, next-day P&L and its decomposition. Takes a few minutes."),
C("%run {SRC}/experiment.py"),
C("""h = pd.read_csv('data/derived/daily_hedge_pnl.csv', parse_dates=['date','start'])
event = h[(h.start >= '2023-03-08') & (h.date <= '2023-03-13')]
cols = ['pnl','pc1','pc2','pc3','curve_resid','other_pnl']
(event.groupby('hedge')[cols].sum()/1e3).round(0).rename(columns={'pnl':'total $k','pc1':'level','pc2':'slope','pc3':'curvature','curve_resid':'other curve','other_pnl':'carry/financing/basis'})"""),
M("### Out-of-sample hedge error\nEach day's hedge uses only that day's prices and the trailing 250-day PCA. Below: standard deviation of daily hedged P&L, whole of Q1 2023 and March only."),
C("""stats = pd.DataFrame({
  'Q1 daily std $k': h.groupby('hedge').pnl.std()/1e3,
  'March daily std $k': h[h.date >= '2023-03-01'].groupby('hedge').pnl.std()/1e3,
  'worst day $k': h.groupby('hedge').pnl.min()/1e3,
  '8-13 Mar total $k': event.groupby('hedge').pnl.sum()/1e3}).round(0)
stats"""),
C("""r = pd.read_csv('data/derived/daily_risk_snapshot.csv', parse_dates=['date']).set_index('date')
r.loc['2023-03-08'].to_frame('8 Mar 2023')"""),
M("## 4. Charts"),
C("""%run {SRC}/figures.py
for f in sorted((ART/'figures').glob('*.png')):
    display(Image(filename=str(f), width=820))"""),
M("## 5. Independent checks\n- Conversion factors and baskets vs CME's table\n- Theoretical futures vs Yahoo Finance daily closes (front contract; third-party data, used only as a check)\n- Our fitted curve vs the Federal Reserve's Gürkaynak–Sack–Wright curve\n- The P&L decomposition adds back to the total"),
C("""%run {SRC}/validation.py"""),
M("""## Limitations (read before using this for anything real)
- Futures are valued at the cheapest-to-deliver forward price with an overnight repo rate (TGCR) held flat to delivery. This ignores the futures seller's delivery options and term-repo, so it overstates the futures price slightly; the check against Yahoo closes shows the size of the gap.
- FedInvest end-of-day prices and futures closes are not taken at the same moment.
- PCA factors are estimated on **par** yields and applied to **zero-rate** key shocks; this is a standard practical shortcut, not an exact mapping.
- Transaction costs and bid/offer are ignored. The note is financed in repo at TGCR."""),
]
nb["cells"] = cells
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "the_hedge_that_leaked.ipynb")
