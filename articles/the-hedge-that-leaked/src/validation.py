"""Independent checks: CME conversion factors and baskets, Yahoo futures prints, the Fed's GSW curve."""
import sys, pickle, json
import os as _os
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[3]   # repo root: data/raw lives there
_os.chdir(ROOT)
sys.path.insert(0, str(_Path(__file__).resolve().parent))
import numpy as np, pandas as pd
from mff_rates import *
from validate_cf import parse_cme_table

out = {}
# 1. Conversion factors vs CME's published table
t = parse_cme_table()
t["our_cf"] = [conversion_factor(r.coupon, r.maturity, r.delivery, r.contract) for r in t.itertuples()]
out["cf_rows"] = int(len(t)); out["cf_exact"] = int((t.our_cf.round(4) == t.cme_cf.round(4)).sum())

# 2. Basket rules vs CME's security list (both directions)
d = pd.read_excel("data/raw/cme_treasury_conversion_factors_TCF_2026-10-21.xlsx", "Security Database", header=None)
sec = d.iloc[4:, [3, 4, 5, 6]].dropna(); sec.columns = ["coupon", "issue", "maturity", "cusip"]
sec = sec[sec.cusip.astype(str).str.match(r"912")]
bk = {}
for c in ["TU", "FV", "TY"]:
    months = sorted(t[t.contract == c].delivery.unique())
    have = set(zip(t[t.contract == c].cusip, t[t.contract == c].delivery))
    ours = {(r.cusip, m) for r in sec.itertuples() for m in months if eligible(c, r.maturity, r.issue, m)}
    bk[c] = dict(cme=len(have), ours=len(ours), only_cme=len(have - ours), only_ours=len(ours - have))
out["baskets"] = bk

# 3. Theoretical futures vs Yahoo Finance daily closes (front contract)
P, A, R = load_fedinvest(), load_auctions(), load_repo("tgcr")
rows = []
for s, c in [("ZT", "TU"), ("ZF", "FV"), ("ZN", "TY")]:
    y = pd.read_csv(f"data/raw/yahoo_{s}_front_continuous_2023Q1.csv", parse_dates=["date"]).set_index("date")["close"]
    for dt in y.index:
        if dt <= pd.Timestamp("2023-02-24"): mon = "2023-03-01"
        elif dt >= pd.Timestamp("2023-03-23"): mon = "2023-06-01"
        else: continue                      # March contract in its delivery month: skip
        if dt not in set(P.date): continue
        u = build_universe(P, A, dt)
        ctd = theoretical_future(u, c, mon, R.asof(dt))[0]
        rows.append(dict(date=dt, contract=c, month=mon[:7], theo=ctd.fut, yahoo=y[dt], ctd=ctd.cusip))
fv = pd.DataFrame(rows); fv["diff_32nds"] = (fv.theo - fv.yahoo) * 32
fv.to_csv("data/derived/futures_vs_yahoo.csv", index=False)
g = fv.groupby(["contract", "month"])["diff_32nds"]
out["futures_vs_yahoo"] = {f"{k[0]} {k[1]}": dict(n=int(v.count()), mean=round(v.mean(), 2), mean_abs=round(v.abs().mean(), 2), max_abs=round(v.abs().max(), 2)) for k, v in g}
dchg = fv.sort_values("date").groupby(["contract", "month"]).apply(lambda x: ((x.theo.diff() - x.yahoo.diff()) * 32).abs().mean())
out["futures_daily_change_mae_32nds"] = {f"{k[0]} {k[1]}": round(v, 2) for k, v in dchg.items()}

# 4. Our curve vs the Fed's GSW curve
fits = pickle.load(open("data/derived/curve_fits.pkl", "rb"))
G = load_gsw()
cv = []
for dt, p in fits.items():
    if dt not in G.index or np.isnan(G.loc[dt, "SVENY02"]): continue
    cv.append({f"{m}y": (svensson_zero(m, p) - G.loc[dt, f"SVENY{m:02d}"] / 100) * 1e4 for m in (2, 5, 10)} | {"date": dt})
cv = pd.DataFrame(cv)
cv.to_csv("data/derived/curve_vs_gsw.csv", index=False)
out["curve_vs_gsw_bp"] = {k: dict(mean=round(cv[k].mean(), 2), mean_abs=round(cv[k].abs().mean(), 2), max_abs=round(cv[k].abs().max(), 2)) for k in ("2y", "5y", "10y")}
out["curve_days"] = int(len(cv))

# 5. P&L decomposition adds up
h = pd.read_csv("data/derived/daily_hedge_pnl.csv")
out["pnl_decomposition_max_gap_usd"] = float((h.pnl - (h.pc1 + h.pc2 + h.pc3 + h.curve_resid + h.other_pnl)).abs().max())
out["krd_vs_full_curve_reval_corr"] = round(float(np.corrcoef(h.krd_pred, h.curve_pnl)[0, 1]), 4)
json.dump(out, open("data/derived/validation_summary.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
