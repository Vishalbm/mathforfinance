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
    bars = ax.bar(cols, d.values, color=S[0], width=0.6)
    for b, v in zip(bars, d.values):
        ax.text(b.get_x() + b.get_width() / 2, v - 4, f"{v:.0f}", ha="center", va="top", color=INK, fontsize=10)
    ax.axhline(0, color=INK2, lw=1)
    ax.set_ylabel("Change in yield (basis points)")
    ax.set_ylim(min(d.values) * 1.2, 10)
    title(ax, "Not a parallel move: short yields fell twice as far as 10s",
          "US Treasury par yields, change from close 8 Mar 2023 to close 13 Mar 2023")
    fig.text(0.01, 0.01, "Source: US Treasury daily par yield curve. mathforfinance.com", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig1_curve_move.png", dpi=160); plt.close(fig)


def fig_krd():
    r = pd.read_csv("data/derived/daily_risk_snapshot.csv", parse_dates=["date"]).set_index("date").loc["2023-03-08"]
    h = pd.read_csv("data/derived/daily_hedge_pnl.csv", parse_dates=["start"])
    n = h[(h.start == "2023-03-08") & (h.hedge == "DV01 with 10y futures (TY)")]["n_TY"].iloc[0]
    keys = ["1y", "2y", "3y", "5y", "7y", "10y"]
    bond = np.array([r[f"bond_krd_{k}"] for k in keys])
    fut = np.array([n * r[f"TY_krd_{k}"] for k in keys])
    x = np.arange(len(keys)); w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.8))
    b1 = ax.bar(x - w / 2 - 0.01, bond, w, color=S[0], label=r"Short \$100mm 5-year note")
    b2 = ax.bar(x + w / 2 + 0.01, fut, w, color=S[1], label=f"Long {n:.0f} 10-year futures (TY)")
    for bars in (b1, b2):
        for b in bars:
            v = b.get_height()
            if abs(v) > 500:
                ax.text(b.get_x() + b.get_width() / 2, v + (900 if v > 0 else -900), f"{v/1e3:+.0f}k",
                        ha="center", va="bottom" if v > 0 else "top", fontsize=10, color=INK)
    ax.axhline(0, color=INK2, lw=1)
    ax.set_xticks(x, [f"{k} key rate" for k in keys])
    ax.yaxis.set_major_formatter(usd)
    ax.set_ylabel(r"\$ P&L if that key rate falls 1bp")
    ax.legend(frameon=False, loc="lower left")
    title(ax, "Same total DV01, different places on the curve",
          f"Key-rate exposure on 8 Mar 2023. Total DV01 nets to zero, but the risk sits at different points")
    fig.text(0.01, 0.01, "Source: mathforfinance.com calculations from Treasury FedInvest prices; TY CTD 3.875% Dec-2029.", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig2_key_rate_risk.png", dpi=160); plt.close(fig)


ORDER = ["DV01 with 10y futures (TY)", "DV01 with 5y futures (FV)", "Key-rate hedge (TU+FV+TY)", "PCA hedge, level+slope (TU+TY)"]
SHORT = {"DV01 with 10y futures (TY)": "DV01 hedge, 10y futures", "DV01 with 5y futures (FV)": "DV01 hedge, 5y futures",
         "Key-rate hedge (TU+FV+TY)": "Key-rate hedge", "PCA hedge, level+slope (TU+TY)": "PCA hedge (2 factors)"}


def fig_cum():
    h = pd.read_csv("data/derived/daily_hedge_pnl.csv", parse_dates=["date", "start"])
    h = h[h.start >= "2023-03-01"]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.axvspan(pd.Timestamp("2023-03-08"), pd.Timestamp("2023-03-13"), color="#f0efec", zorder=0)
    ax.text(pd.Timestamp("2023-03-08 06:00"), 0.97, "SVB fails", transform=ax.get_xaxis_transform(), fontsize=9.5, color=INK2, va="top")
    for i, name in enumerate(ORDER):
        s = h[h.hedge == name].set_index("date")["pnl"].cumsum()
        s = pd.concat([pd.Series({pd.Timestamp("2023-03-01"): 0.0}), s])
        ax.plot(s.index, s.values, color=S[i], lw=2, label=SHORT[name])
        ax.text(s.index[-1] + pd.Timedelta(hours=10), s.values[-1], SHORT[name], color=INK, fontsize=9.5, va="center")
    ax.axhline(0, color=INK2, lw=1)
    ax.yaxis.set_major_formatter(usd)
    ax.set_xlim(pd.Timestamp("2023-03-01"), pd.Timestamp("2023-04-07"))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d %b"))
    ax.set_ylabel("Cumulative P&L of hedged position")
    ax.legend(frameon=False, loc="lower left", fontsize=9.5)
    title(ax, "When the curve twisted, the 10-year DV01 hedge leaked most",
          r"Short \$100mm on-the-run 5-year note, hedge rebalanced daily, March 2023 (unhedged: -\$2.5mm for the month)")
    fig.text(0.01, 0.01, "Futures valued from cheapest-to-deliver forward prices (no delivery option). Source: mathforfinance.com", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("articles/the-hedge-that-leaked/figures/fig3_cumulative_pnl.png", dpi=160); plt.close(fig)


def fig_waterfall():
    h = pd.read_csv("data/derived/daily_hedge_pnl.csv", parse_dates=["date", "start"])
    w = h[(h.start >= "2023-03-08") & (h.date <= "2023-03-13") & (h.hedge == ORDER[0])].sum(numeric_only=True)
    parts = [("Level\n(PC1)", w.pc1), ("Slope\n(PC2)", w.pc2), ("Curvature\n(PC3)", w.pc3),
             ("Other curve\nshape", w.curve_resid), ("Carry, financing\n& basis", w.other_pnl)]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    run = 0.0
    for i, (lab, v) in enumerate(parts):
        ax.bar(i, v, bottom=run, color=GAIN if v >= 0 else LOSS, width=0.62)
        ax.text(i, run + v + (12000 if v >= 0 else -12000), f"{v/1e3:+,.0f}k", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=10, color=INK)
        run += v
    ax.bar(len(parts), run, color=NEUT, width=0.62)
    ax.text(len(parts), run - 12000, f"{run/1e3:+,.0f}k", ha="center", va="top", fontsize=10, color=INK, fontweight="bold")
    ax.set_xticks(range(len(parts) + 1), [p[0] for p in parts] + ["Total"])
    ax.axhline(0, color=INK2, lw=1)
    ax.yaxis.set_major_formatter(usd)
    ax.set_ylim(run * 1.35, max(60000, run * -0.25))
    title(ax, "Where the money went: the slope of the curve",
          "P&L of the DV01-matched 10-year futures hedge, close 8 Mar to close 13 Mar 2023")
    fig.text(0.01, 0.01, "Factors from PCA of daily Treasury par-yield changes over the prior 250 days. Source: mathforfinance.com", fontsize=8.5, color=INK2)
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
