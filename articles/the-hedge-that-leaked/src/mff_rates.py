"""Building blocks for 'The Hedge That Leaked' (mathforfinance.com).

Everything here is computed from the raw files in data/raw:
Treasury FedInvest prices, Treasury par curve, the Fed's GSW curve,
NY Fed repo rates, TreasuryDirect auction records and CME conversion factors.
"""
from __future__ import annotations
import os as _os
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[3]   # repo root: data/raw lives there
_os.chdir(ROOT)
import math
from dataclasses import dataclass
from datetime import date
import numpy as np
import pandas as pd
import QuantLib as ql
from scipy.optimize import least_squares

RAW = "data/raw"

# ---------------------------------------------------------------- loading
def load_fedinvest(months=("2023-01", "2023-02", "2023-03")) -> pd.DataFrame:
    df = pd.concat([pd.read_csv(f"{RAW}/fedinvest_prices_{m}.csv") for m in months])
    df["date"] = pd.to_datetime(df["date"])
    df["maturity_date"] = pd.to_datetime(df["maturity_date"], format="%m/%d/%Y")
    df = df[df["end_of_day"] > 0]
    return df.rename(columns={"rate_pct": "coupon", "end_of_day": "clean"})


def load_auctions() -> pd.DataFrame:
    a = pd.read_csv(f"{RAW}/treasurydirect_auctions_notes_bonds_2010_2023Q1.csv")
    for c in ["issue_date", "original_issue_date", "dated_date", "maturity_date"]:
        a[c] = pd.to_datetime(a[c], errors="coerce")
    a["first_issue"] = a["original_issue_date"].fillna(a["issue_date"])
    g = a.sort_values("issue_date").groupby("cusip").agg(
        first_issue=("first_issue", "min"), dated_date=("dated_date", "first"),
        maturity_date=("maturity_date", "first"), coupon=("interest_rate", "first"),
        original_term=("original_security_term", "first"), security_term=("security_term", "first"))
    return g.reset_index()


def load_par_curve() -> pd.DataFrame:
    frames = []
    for y in (2021, 2022, 2023):
        d = pd.read_csv(f"{RAW}/treasury_par_yield_curve_{y}.csv")
        d["Date"] = pd.to_datetime(d["Date"], format="%m/%d/%Y")
        frames.append(d)
    p = pd.concat(frames).set_index("Date").sort_index()
    p.columns = [c.replace(" Mo", "M").replace(" Yr", "Y") for c in p.columns]
    return p


def load_gsw() -> pd.DataFrame:
    g = pd.read_csv(f"{RAW}/fed_gsw_nominal_curve_2021_2023H1.csv", na_values="NA")
    g["Date"] = pd.to_datetime(g["Date"])
    return g.set_index("Date")


def load_repo(name="tgcr") -> pd.Series:
    r = pd.read_csv(f"{RAW}/nyfed_{name}_2023.csv", parse_dates=["date"]).set_index("date")["rate_pct"]
    return r.sort_index() / 100.0

# ---------------------------------------------------------------- bonds
def qd(d) -> ql.Date:
    d = pd.Timestamp(d)
    return ql.Date(d.day, d.month, d.year)


CAL = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
DC = ql.ActualActual(ql.ActualActual.Bond)


@dataclass
class Bond:
    cusip: str
    coupon: float          # percent
    maturity: pd.Timestamp
    dated: pd.Timestamp     # start of the coupon schedule

    def ql_bond(self) -> ql.FixedRateBond:
        sched = ql.Schedule(qd(self.dated), qd(self.maturity), ql.Period(ql.Semiannual), CAL,
                            ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, True)
        return ql.FixedRateBond(1, 100.0, sched, [self.coupon / 100.0], DC)

    def cashflows(self, settle: pd.Timestamp):
        """(time in years from settle, amount) for flows after settle, per 100 face."""
        b = self.ql_bond()
        out = []
        for cf in b.cashflows():
            d = pd.Timestamp(cf.date().year(), cf.date().month(), cf.date().dayOfMonth())
            if d > settle:
                out.append(((d - settle).days / 365.25, cf.amount()))
        return np.array(out)

    def accrued(self, settle: pd.Timestamp) -> float:
        return self.ql_bond().accruedAmount(qd(settle))

    def yld(self, clean: float, settle: pd.Timestamp) -> float:
        b = self.ql_bond()
        return b.bondYield(ql.BondPrice(clean, ql.BondPrice.Clean), DC, ql.Compounded, ql.Semiannual, qd(settle))

    def clean_from_yield(self, y: float, settle: pd.Timestamp) -> float:
        b = self.ql_bond()
        return b.cleanPrice(y, DC, ql.Compounded, ql.Semiannual, qd(settle))

    def dv01(self, clean: float, settle: pd.Timestamp) -> float:
        """Dollar value of 1bp per 100 face (price change, dirty), via +/-1bp yield bump."""
        y = self.yld(clean, settle)
        up = self.clean_from_yield(y + 1e-4, settle)
        dn = self.clean_from_yield(y - 1e-4, settle)
        return (dn - up) / 2.0


def settle_date(trade: pd.Timestamp) -> pd.Timestamp:
    d = CAL.advance(qd(trade), 1, ql.Days)
    return pd.Timestamp(d.year(), d.month(), d.dayOfMonth())

# ---------------------------------------------------------------- CME conversion factors
QUARTERLY = {"TY", "TN", "US", "UB", "TWE"}


def conversion_factor(coupon_pct: float, maturity: pd.Timestamp, delivery_month_first_day: pd.Timestamp, contract: str) -> float:
    """CME/CBOT conversion factor: price per 1 of par at a 6% yield (CME, 'Calculating U.S.
    Treasury Futures Conversion Factors', 2024)."""
    c = math.floor(coupon_pct / 100 * 8 * 100 + 0.5 + 1e-9) / 800  # nearest 1/8 of 1%
    d0 = pd.Timestamp(delivery_month_first_day)
    m = pd.Timestamp(maturity)
    months = (m.year - d0.year) * 12 + (m.month - d0.month) - (1 if m.day < d0.day else 0)
    n, z = divmod(months, 12)
    if contract in QUARTERLY:
        z = (z // 3) * 3
    v = z if z < 7 else z - 6
    a = 1 / 1.03 ** (v / 6)
    b = (c / 2) * (6 - v) / 6
    cc = 1 / 1.03 ** (2 * n) if z < 7 else 1 / 1.03 ** (2 * n + 1)
    d = (c / 0.06) * (1 - cc)
    return round(a * ((c / 2) + cc + d) - b, 4)


# ---------------------------------------------------------------- deliverable baskets (CME, Exhibit 1)
def _add(d, years=0, months=0):
    return pd.Timestamp(d) + pd.DateOffset(years=years, months=months)


def eligible(contract: str, maturity, first_issue, delivery_first_day) -> bool:
    m, iss, d0 = pd.Timestamp(maturity), pd.Timestamp(first_issue), pd.Timestamp(delivery_first_day)
    d_last = d0 + pd.offsets.MonthEnd(0)
    orig_ok_5y3m = m <= _add(iss, 5, 3) + pd.Timedelta(days=7)  # tolerance for issue-date slippage
    if contract == "TU":
        return orig_ok_5y3m and m >= _add(d0, 1, 9) and m <= _add(d_last, 2, 0)
    if contract == "FV":
        return orig_ok_5y3m and m >= _add(d0, 4, 2)
    if contract == "TY":
        is_note = m <= _add(iss, 10, 0) + pd.Timedelta(days=7)  # notes only: original term <= 10y
        return is_note and m >= _add(d0, 6, 6) and m < _add(d0, 8, 0)
    raise ValueError(contract)


# ---------------------------------------------------------------- curve fitting (Svensson, as in Gurkaynak-Sack-Wright 2007)
def svensson_zero(t, p):
    b0, b1, b2, b3, t1, t2 = p
    t = np.maximum(np.asarray(t, float), 1e-6)
    x1, x2 = t / t1, t / t2
    f1 = (1 - np.exp(-x1)) / x1
    return b0 + b1 * f1 + b2 * (f1 - np.exp(-x1)) + b3 * ((1 - np.exp(-x2)) / x2 - np.exp(-x2))


def build_universe(prices: pd.DataFrame, auctions: pd.DataFrame, trade_date) -> pd.DataFrame:
    """All fixed-coupon notes/bonds priced on trade_date that we can reconstruct from auction records."""
    td = pd.Timestamp(trade_date)
    p = prices[prices["date"] == td].merge(auctions[["cusip", "first_issue", "dated_date", "original_term"]], on="cusip", how="inner")
    st = settle_date(td)
    rows = []
    for r in p.itertuples():
        b = Bond(r.cusip, r.coupon, r.maturity_date, r.dated_date)
        acc = b.accrued(st)
        rows.append(dict(cusip=r.cusip, coupon=r.coupon, maturity=r.maturity_date, first_issue=r.first_issue,
                         original_term=r.original_term, clean=r.clean, accrued=acc, dirty=r.clean + acc,
                         ttm=(r.maturity_date - st).days / 365.25, bond=b))
    u = pd.DataFrame(rows)
    u["settle"] = st
    return u


def fit_svensson(u: pd.DataFrame, min_ttm=1.0, max_ttm=30.0):
    """Fit Svensson zero curve (continuously compounded) to dirty prices; weights ~ 1/duration (approx. yield errors)."""
    v = u[(u.ttm >= min_ttm) & (u.ttm <= max_ttm)].copy()
    st = v["settle"].iloc[0]
    flows = [r.bond.cashflows(st) for r in v.itertuples()]
    dirty = v["dirty"].to_numpy()
    w = 1.0 / np.maximum(v["ttm"].to_numpy(), 0.5)

    def model(p):
        return np.array([np.sum(f[:, 1] * np.exp(-svensson_zero(f[:, 0], p) * f[:, 0])) for f in flows])

    def resid(p):
        return (model(p) - dirty) * w

    best = None
    for t1, t2 in [(1.5, 8.0), (1.0, 5.0), (2.5, 12.0), (0.7, 3.0)]:
        x0 = [0.04, 0.0, 0.0, 0.0, t1, t2]
        r = least_squares(resid, x0, bounds=([-0.1, -0.2, -0.5, -0.5, 0.1, 0.1], [0.2, 0.2, 0.5, 0.5, 30, 30]))
        if best is None or r.cost < best.cost:
            best = r
    v["model_dirty"] = model(best.x)
    v["price_err"] = v["model_dirty"] - v["dirty"]
    return best.x, v


def dirty_from_zero(flows, zero_fn, spread=0.0):
    return float(np.sum(flows[:, 1] * np.exp(-(zero_fn(flows[:, 0]) + spread) * flows[:, 0])))


def solve_spread(flows, zero_fn, dirty):
    from scipy.optimize import brentq
    return brentq(lambda s: dirty_from_zero(flows, zero_fn, s) - dirty, -0.05, 0.05)


# ---------------------------------------------------------------- key-rate shocks
KEYS = np.array([2.0, 5.0, 10.0, 30.0])


def key_shape(t, k_idx, keys=KEYS):
    """Triangular key-rate bump (Ho 1992): 1 at keys[k], linear to 0 at neighbours, flat at the ends."""
    t = np.asarray(t, float)
    k = keys[k_idx]
    lo = keys[k_idx - 1] if k_idx > 0 else None
    hi = keys[k_idx + 1] if k_idx < len(keys) - 1 else None
    out = np.zeros_like(t)
    left = t <= k
    out[left] = 1.0 if lo is None else np.clip((t[left] - lo) / (k - lo), 0, 1)
    right = t > k
    out[right] = 1.0 if hi is None else np.clip((hi - t[right]) / (hi - k), 0, 1)
    return out


# ---------------------------------------------------------------- futures (theoretical, no delivery option)
def delivery_days(delivery_first_day):
    d0 = pd.Timestamp(delivery_first_day)
    first = CAL.adjust(qd(d0), ql.Following)
    last = CAL.adjust(qd(d0 + pd.offsets.MonthEnd(0)), ql.Preceding)
    f = lambda x: pd.Timestamp(x.year(), x.month(), x.dayOfMonth())
    return f(first), f(last)


def forward_clean(bond: Bond, dirty: float, settle, deliver, repo: float) -> float:
    """Repo-financed forward clean price (ACT/360 simple repo, coupons reinvested at repo)."""
    settle, deliver = pd.Timestamp(settle), pd.Timestamp(deliver)
    fwd = dirty * (1 + repo * (deliver - settle).days / 360)
    for cf in bond.ql_bond().cashflows():
        d = pd.Timestamp(cf.date().year(), cf.date().month(), cf.date().dayOfMonth())
        if settle < d <= deliver:
            fwd -= cf.amount() * (1 + repo * (deliver - d).days / 360)
    return fwd - bond.accrued(deliver)


def theoretical_future(u: pd.DataFrame, contract: str, delivery_first_day, repo: float):
    """Cheapest of forward_clean/CF over the basket and over {first, last} delivery day.
    Ignores the short's timing/quality options, so it is an upper bound on the fair futures price."""
    d0 = pd.Timestamp(delivery_first_day)
    first, last = delivery_days(d0)
    st = u["settle"].iloc[0]
    rows = []
    for r in u.itertuples():
        if not eligible(contract, r.maturity, r.first_issue, d0):
            continue
        cf = conversion_factor(r.coupon, r.maturity, d0, contract)
        for D in {max(first, st), max(last, st)}:
            fc = forward_clean(r.bond, r.dirty, st, D, repo)
            rows.append(dict(cusip=r.cusip, coupon=r.coupon, maturity=r.maturity, cf=cf, deliver=D,
                             fwd_clean=fc, fut=fc / cf, carry_factor=1 + repo * (D - st).days / 360))
    b = pd.DataFrame(rows).sort_values("fut")
    return b.iloc[0], b
