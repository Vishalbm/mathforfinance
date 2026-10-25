"""Daily hedge experiment, Q1 2023: long $100mm of the on-the-run 10-year note, hedged with Treasury futures.

Run:  python src/experiment.py   -> writes data/derived/*.csv
"""
import sys, pickle, os
import os as _os
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[3]   # repo root: data/raw lives there
_os.chdir(ROOT)
sys.path.insert(0, str(_Path(__file__).resolve().parent))
import numpy as np
import pandas as pd
from mff_rates import *

FACE = 100e6            # $100mm face
SIDE = +1               # +1 = long the note, -1 = short
FUTS = ("FV", "TY", "TN")   # 5-year, "10-year" (trades like a 7-year), Ultra 10-year (UXY)
FUT_MULT = 1000.0       # $ per point per contract ($100k notional)
os.makedirs("data/derived", exist_ok=True)

P, A, R = load_fedinvest(), load_auctions(), load_repo("tgcr")
PAR = load_par_curve()
DATES = sorted(P["date"].unique())
DATES = [pd.Timestamp(d) for d in DATES if pd.Timestamp(d) >= pd.Timestamp("2023-01-03")]
DATES = [d for d in DATES if d in PAR.index]   # Treasury business days only


def contract_month(t):
    return pd.Timestamp("2023-03-01") if t <= pd.Timestamp("2023-02-24") else pd.Timestamp("2023-06-01")


def otr_10y(t):
    a = A[(A["original_term"] == "10-Year") & (A["first_issue"] <= t)]
    return a.sort_values("first_issue").iloc[-1]["cusip"]


CACHE = "data/derived/curve_fits.pkl"
fits = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}


def day_state(t):
    u = build_universe(P, A, t)
    if t not in fits:
        fits[t] = fit_svensson(u)[0]
    p = fits[t]
    return u, p


def zero_fn(p, bump=None):
    if bump is None:
        return lambda tt: svensson_zero(tt, p)
    k, size = bump
    return lambda tt: svensson_zero(tt, p) + size * key_shape(tt, k)


def instrument_snapshot(u, p, repo, cusip_pos, month):
    """Prices, KRDs (per bp, per 100 face / per 100 futures notional) and the objects needed to reprice."""
    st = u["settle"].iloc[0]
    z = zero_fn(p)
    out = {}
    # the 10-year note
    r = u[u.cusip == cusip_pos].iloc[0]
    fl = r.bond.cashflows(st)
    s = solve_spread(fl, z, r.dirty)
    krd = np.array([-(dirty_from_zero(fl, zero_fn(p, (k, 1e-4)), s) - r.dirty) for k in range(len(KEYS))])
    out["BOND"] = dict(price=r.dirty, krd=krd, cusip=cusip_pos, spread=s)
    # futures, CTD held fixed for sensitivities
    for c in FUTS:
        ctd, basket = theoretical_future(u, c, month, repo)
        cr = u[u.cusip == ctd.cusip].iloc[0]
        cfl = cr.bond.cashflows(st)
        cs = solve_spread(cfl, z, cr.dirty)
        k_ctd = np.array([-(dirty_from_zero(cfl, zero_fn(p, (k, 1e-4)), cs) - cr.dirty) for k in range(len(KEYS))])
        out[c] = dict(price=ctd.fut, krd=k_ctd * ctd.carry_factor / ctd.cf, cusip=ctd.cusip, cf=ctd.cf,
                      deliver=ctd.deliver, spread=cs, carry=ctd.carry_factor)
    return out


def pca_loadings(t, window=250):
    cols = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
    h = PAR.loc[:t, cols].dropna().diff().dropna().iloc[-window:] / 100.0   # decimal
    cov = np.cov(h.to_numpy().T)
    w, v = np.linalg.eigh(cov)
    idx = np.argsort(w)[::-1]
    w, v = w[idx], v[:, idx]
    for i in range(3):                       # sign convention: PC1 up = rates up, PC2 up = steepening
        if i == 0 and v[:, 0].sum() < 0: v[:, 0] *= -1
        if i == 1 and v[-1, 1] - v[1, 1] < 0: v[:, 1] *= -1
        if i == 2 and v[3, 2] < 0: v[:, 2] *= -1
    L = pd.DataFrame(v[:, :3], index=cols, columns=["PC1", "PC2", "PC3"])
    expl = w[:3] / w.sum()
    return L, expl


def hedge_ratios(snap, L):
    """Number of futures contracts (positive = long) for each hedge style."""
    # all exposures are "$ P&L if that key rate falls 1bp"
    pos = SIDE * FACE / 100 * snap["BOND"]["krd"]
    f = {c: FUT_MULT * snap[c]["krd"] for c in FUTS}          # per long contract
    dv = lambda x: x.sum()
    H = {"Unhedged": {}}
    H["DV01 hedge, TY"] = {"TY": -dv(pos) / dv(f["TY"])}
    H["DV01 hedge, UXY"] = {"TN": -dv(pos) / dv(f["TN"])}
    # key-rate hedge: match risk in three buckets (1-5y -> FV, 7y -> TY, 10-30y -> UXY)
    B = np.array([[1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1]], float)
    M = np.column_stack([B @ f[c] for c in FUTS])
    n = np.linalg.solve(M, -(B @ pos))
    H["Key-rate hedge (FV+TY+UXY)"] = dict(zip(FUTS, n))
    Lk = L[["PC1", "PC2"]].to_numpy()                                      # loadings at the key tenors
    E = lambda krd: krd @ Lk                                             # $ per 1-unit factor move (in bp)
    M2 = np.column_stack([E(f["FV"]), E(f["TN"])])
    n2 = np.linalg.solve(M2, -E(pos))
    H["PCA hedge, level+slope (FV+UXY)"] = dict(zip(("FV", "TN"), n2))
    return H, pos, f


def reprice(snap_t, u1, p1, repo_t, month, curve_only):
    """Value instruments at t+1. curve_only=True: t+1 curve, but t spreads / CTD / repo / delivery date."""
    st1 = u1["settle"].iloc[0]
    z1 = zero_fn(p1)
    out = {}
    b = snap_t["BOND"]
    r = u1[u1.cusip == b["cusip"]].iloc[0]
    coupons = 0.0
    st0 = snap_t["_settle"]
    for cf in r.bond.ql_bond().cashflows():
        d = pd.Timestamp(cf.date().year(), cf.date().month(), cf.date().dayOfMonth())
        if st0 < d <= st1:
            coupons += cf.amount()
    out["BOND"] = (dirty_from_zero(r.bond.cashflows(st1), z1, b["spread"]) if curve_only else r.dirty) + coupons
    for c in FUTS:
        s = snap_t[c]
        if curve_only:
            cr = u1[u1.cusip == s["cusip"]].iloc[0]
            d1 = dirty_from_zero(cr.bond.cashflows(st1), z1, s["spread"])
            out[c] = forward_clean(cr.bond, d1, st1, s["deliver"], repo_t) / s["cf"]
        else:
            out[c] = theoretical_future(u1, c, month, R.asof(st1 - pd.Timedelta(days=1)))[0].fut
    return out


def main():
    rows, krd_rows, att_rows = [], [], []
    state = {}
    for t in DATES:
        state[t] = day_state(t)
    pickle.dump(fits, open(CACHE, "wb"))
    for t0, t1 in zip(DATES[:-1], DATES[1:]):
        u0, p0 = state[t0]; u1, p1 = state[t1]
        repo0 = R.asof(t0)
        month = contract_month(t0)
        cus = otr_10y(t0)
        snap = instrument_snapshot(u0, p0, repo0, cus, month)
        snap["_settle"] = u0["settle"].iloc[0]
        L, expl = pca_loadings(t0)
        H, pos, f = hedge_ratios(snap, L)
        full = reprice(snap, u1, p1, repo0, month, curve_only=False)
        curve = reprice(snap, u1, p1, repo0, month, curve_only=True)
        dz = np.array([svensson_zero(k, p1) - svensson_zero(k, p0) for k in KEYS]) * 1e4   # bp, zero rates
        Lk = L.to_numpy()
        cols = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
        dpar = (PAR.loc[t1, cols] - PAR.loc[t0, cols]).to_numpy() * 100                    # bp, official par yields
        fac = Lk.T @ dpar                                                                  # factor moves (bp units)
        for name, h in H.items():
            def pnl(px):
                v = SIDE * FACE / 100 * (px["BOND"] - snap["BOND"]["price"])
                for c, n in h.items():
                    v += n * FUT_MULT * (px[c] - snap[c]["price"])
                return v
            # the note is financed in repo: a long pays repo on the cash borrowed (a short would earn it)
            days = (u1["settle"].iloc[0] - snap["_settle"]).days
            financing = -SIDE * FACE / 100 * snap["BOND"]["price"] * repo0 * days / 360
            tot, cur = pnl(full) + financing, pnl(curve)
            net = pos + sum(n * f[c] for c, n in h.items())
            exp_pc = net @ Lk                                     # risk ($ lost per +1bp of each factor)
            parts = -exp_pc * fac                                 # P&L = -risk x move
            krd_pred = -(net * dz).sum()                          # first-order key-rate prediction
            rows.append(dict(date=t1, start=t0, hedge=name, pnl=tot, curve_pnl=cur, other_pnl=tot - cur,
                             pc1=parts[0], pc2=parts[1], pc3=parts[2], curve_resid=cur - parts.sum(), krd_pred=krd_pred,
                             net_dv01=net.sum(), **{f"n_{c}": h.get(c, 0.0) for c in FUTS}))
        krd_rows.append(dict(date=t0, cusip=cus, contract=month.strftime("%b%y"),
                             **{f"bond_krd_{int(k)}y": SIDE * FACE / 100 * snap["BOND"]["krd"][i] for i, k in enumerate(KEYS)},
                             **{f"{c}_krd_{int(k)}y": FUT_MULT * snap[c]["krd"][i] for c in FUTS for i, k in enumerate(KEYS)},
                             **{f"{c}_ctd": snap[c]["cusip"] for c in FUTS},
                             **{f"{c}_price": snap[c]["price"] for c in FUTS},
                             pc_explained=",".join(f"{x:.3f}" for x in expl),
                             **{f"dz_{int(k)}y_next": dz[i] for i, k in enumerate(KEYS)},
                             **{f"f{i+1}_next": fac[i] for i in range(3)}))
        print(t0.date(), cus, month.strftime("%b%y"), "done", flush=True)
    pd.DataFrame(rows).to_csv("data/derived/daily_hedge_pnl.csv", index=False)
    pd.DataFrame(krd_rows).to_csv("data/derived/daily_risk_snapshot.csv", index=False)


if __name__ == "__main__":
    main()
