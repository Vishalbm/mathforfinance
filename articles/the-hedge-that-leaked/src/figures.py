"""Charts for 'The Hedge That Leaked'. Colours: validated reference palette (light surface)."""
import sys
import os as _os
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[3]   # repo root: data/raw lives there
_os.chdir(ROOT)

sys.path.insert(0, str(_Path(__file__).resolve().parent))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from mff_rates import load_par_curve

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
GAIN, LOSS, NEUT = "#2a78d6", "#e34948", "#8a8984"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
                     "font.family": "DejaVu Sans"})
usd = FuncFormatter(lambda x, _: f"-${abs(x)/1e3:,.0f}k" if x < 0 else f"${x/1e3:,.0f}k")


def title(ax, t, sub):
    ax.set_title(t, loc="left", fontsize=14, fontweight="bold", color=INK, pad=26)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10.5, color=INK2, va="bottom")


def fig_curve_move():
    p = load_par_curve()
    cols = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
    d = (p.loc["2023-03-13", cols] - p.loc["2023-03-08", cols]) * 100
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colors = [S[1] if c in ("7Y", "10Y") else "#9db9e0" for c in cols]
    bars = ax.bar(cols, d.values, color=colors, width=0.6)
    for b, v in zip(bars, d.values):
        ax.text(b.get_x() + b.get_width() / 2, v - 4, f"{v:.0f}", ha="center", va="top", color=INK, fontsize=10)
    ax.axhline(0, color=INK2, lw=1)
    ax.set_ylabel("Change in yield (basis points)")
    ax.set_ylim(min(d.values) * 1.2, 10)
    title(ax, "Not a parallel move: the 7-year fell 11bp more than the 10-year",
          "US Treasury par yields, change from close 8 Mar 2023 to close 13 Mar 2023")
    fig.text(0.01, 0.01, "Source: US Treasury daily par yield curve. mathforfinance.com", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig1_curve_move.png", dpi=160); plt.close(fig)


ORDER = ["DV01 hedge, TY", "DV01 hedge, UXY", "Key-rate hedge (FV+TY+UXY)", "PCA hedge, level+slope (FV+UXY)"]
SHORT = {"DV01 hedge, TY": "DV01 hedge, TY", "DV01 hedge, UXY": "DV01 hedge, UXY",
         "Key-rate hedge (FV+TY+UXY)": "Key-rate hedge", "PCA hedge, level+slope (FV+UXY)": "PCA hedge (2 factors)"}
KEYS_ALL = [1, 2, 3, 5, 7, 10, 20, 30]


def fig_krd():
    r = pd.read_csv("data/derived/daily_risk_snapshot.csv", parse_dates=["date"]).set_index("date").loc["2023-03-08"]
    h = pd.read_csv("data/derived/daily_hedge_pnl.csv", parse_dates=["start"])
    n = h[(h.start == "2023-03-08") & (h.hedge == ORDER[0])]["n_TY"].iloc[0]
    keys = ["1y", "2y", "3y", "5y", "7y", "10y"]
    bond = np.array([r[f"bond_krd_{k}"] for k in keys])
    fut = np.array([n * r[f"TY_krd_{k}"] for k in keys])
    x = np.arange(len(keys)); w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.8))
    b1 = ax.bar(x - w / 2 - 0.01, bond, w, color=S[0], label=r"Long \$100mm 10-year note")
    b2 = ax.bar(x + w / 2 + 0.01, fut, w, color=S[1], label=f"Short {abs(n):.0f} TY futures")
    for bars in (b1, b2):
        for b in bars:
            v = b.get_height()
            if abs(v) > 1500:
                ax.text(b.get_x() + b.get_width() / 2, v + (1500 if v > 0 else -1500), f"{v/1e3:+.0f}k",
                        ha="center", va="bottom" if v > 0 else "top", fontsize=10, color=INK)
    ax.axhline(0, color=INK2, lw=1)
    ax.set_xticks(x, [f"{k} key rate" for k in keys])
    ax.yaxis.set_major_formatter(usd)
    ax.set_ylabel(r"\$ P&L if that key rate falls 1bp")
    ax.legend(frameon=False, loc="lower left")
    title(ax, "Same total DV01, different places on the curve",
          "Key-rate exposure on 8 Mar 2023. The note's risk sits at 10 years; TY's sits at 7 years")
    fig.text(0.01, 0.01, "Source: mathforfinance.com calculations from Treasury FedInvest prices; June 2023 TY CTD: 3.875% Dec-2029.", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig2_key_rate_risk.png", dpi=160); plt.close(fig)


def fig_cum():
    h = pd.read_csv("data/derived/daily_hedge_pnl.csv", parse_dates=["date", "start"])
    h = h[h.start >= "2023-03-01"]
    unh = h[h.hedge == "Unhedged"].pnl.sum()
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.axvspan(pd.Timestamp("2023-03-08"), pd.Timestamp("2023-03-13"), color="#f0efec", zorder=0)
    ax.text(pd.Timestamp("2023-03-08 06:00"), 0.97, "SVB fails", transform=ax.get_xaxis_transform(), fontsize=9.5, color=INK2, va="top")
    for i, name in enumerate(ORDER):
        s = h[h.hedge == name].set_index("date")["pnl"].cumsum()
        s = pd.concat([pd.Series({pd.Timestamp("2023-03-01"): 0.0}), s])
        ax.plot(s.index, s.values, color=S[i], lw=2, label=SHORT[name])
    ax.axhline(0, color=INK2, lw=1)
    ax.yaxis.set_major_formatter(usd)
    ax.set_xlim(pd.Timestamp("2023-03-01"), pd.Timestamp("2023-03-31"))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d %b"))
    ax.set_ylabel("Cumulative P&L of hedged position")
    ax.legend(frameon=False, loc="lower left", fontsize=9.5)
    title(ax, "Hedging the 10-year with TY leaked; UXY held",
          rf"Long \$100mm 10-year note, hedges rebalanced daily. Unhedged, the note made +\${unh/1e6:.1f}mm in March")
    fig.text(0.01, 0.01, "Futures valued from cheapest-to-deliver forward prices (no delivery option). Source: mathforfinance.com", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig3_cumulative_pnl.png", dpi=160); plt.close(fig)


def waterfall_parts(hedge=ORDER[0], start="2023-03-08", end="2023-03-13"):
    """Split the hedge's P&L by key rate: net key-rate exposure x fall in that zero rate, summed daily."""
    h = pd.read_csv("data/derived/daily_hedge_pnl.csv", parse_dates=["date", "start"])
    r = pd.read_csv("data/derived/daily_risk_snapshot.csv", parse_dates=["date"]).set_index("date")
    w = h[(h.start >= start) & (h.date <= end) & (h.hedge == hedge)]
    by_key = {k: 0.0 for k in KEYS_ALL}
    for row in w.itertuples():
        s = r.loc[row.start]
        for k in KEYS_ALL:
            net = s[f"bond_krd_{k}y"] + sum(getattr(row, f"n_{c}") * s[f"{c}_krd_{k}y"] for c in ("FV", "TY", "TN"))
            by_key[k] += net * (-s[f"dz_{k}y_next"])
    tot = w.sum(numeric_only=True)
    parts = [("1-5y key\nrates", sum(by_key[k] for k in (1, 2, 3, 5))), ("7y key\nrate", by_key[7]),
             ("10-30y key\nrates", sum(by_key[k] for k in (10, 20, 30))),
             ("Convexity &\ncurve shape", tot.curve_pnl - tot.krd_pred), ("Carry, financing\n& basis", tot.other_pnl)]
    return parts, tot.pnl


def fig_waterfall():
    parts, total = waterfall_parts()
    assert abs(sum(v for _, v in parts) - total) < 1.0
    fig, ax = plt.subplots(figsize=(9.5, 5))
    run = 0.0
    span = max(abs(v) for _, v in parts)
    off = span * 0.03
    for i, (lab, v) in enumerate(parts):
        ax.bar(i, v, bottom=run, color=GAIN if v >= 0 else LOSS, width=0.62)
        ax.text(i, run + v + (off if v >= 0 else -off), f"{v/1e3:+,.0f}k", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=10, color=INK)
        run += v
    ax.bar(len(parts), run, color=NEUT, width=0.62)
    ax.text(len(parts), run - off, f"{run/1e3:+,.0f}k", ha="center", va="top", fontsize=10, color=INK, fontweight="bold")
    ax.set_xticks(range(len(parts) + 1), [p[0] for p in parts] + ["Total"])
    ax.axhline(0, color=INK2, lw=1)
    ax.yaxis.set_major_formatter(usd)
    lo = min(0, min(np.cumsum([v for _, v in parts]))) ; hi = max(0, max(np.cumsum([v for _, v in parts])))
    ax.set_ylim(lo - span * 0.25, hi + span * 0.2)
    title(ax, "Where the money went: long 10s, short 7s",
          "P&L of the 10-year note hedged with TY at zero DV01, close 8 Mar to close 13 Mar 2023")
    fig.text(0.01, 0.01, "Each key rate: net exposure x fall in that zero rate, summed daily. Source: mathforfinance.com", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig4_waterfall.png", dpi=160); plt.close(fig)


def fig_pca():
    sys.argv = [""]
    from experiment import pca_loadings
    L, expl = pca_loadings(pd.Timestamp("2023-03-08"))
    tn = [1, 2, 3, 5, 7, 10, 20, 30]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    names = ["Level", "Slope", "Curvature"]
    for i, c in enumerate(["PC1", "PC2", "PC3"]):
        ax.plot(tn, L[c].values, color=S[i], lw=2, marker="o", ms=5, label=f"{names[i]} ({expl[i]*100:.0f}% of variance)")
        ax.text(30.6, L[c].values[-1], names[i], color=INK, fontsize=10, va="center")
    ax.axhline(0, color=INK2, lw=1)
    ax.set_xscale("log"); ax.set_xticks(tn, [f"{t}y" for t in tn]); ax.minorticks_off()
    ax.set_xlim(0.9, 40)
    ax.set_ylabel("Loading (weight on each tenor)")
    ax.legend(frameon=False, loc="lower left")
    title(ax, "Three shapes explain how the Treasury curve moves",
          "Principal components of daily par-yield changes, 250 days to 8 Mar 2023")
    fig.text(0.01, 0.01, "Source: US Treasury daily par yield curve; mathforfinance.com", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig5_pca_shapes.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    fig_curve_move(); fig_krd(); fig_cum(); fig_waterfall(); fig_pca(); print("ok")
