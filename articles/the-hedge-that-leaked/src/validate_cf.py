"""Check our conversion-factor formula against CME's published table (data/raw/cme_treasury_conversion_factors_TCF_2026-10-21.xlsx)."""
import sys, re
import os as _os
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[3]   # repo root: data/raw lives there
_os.chdir(ROOT)
import pandas as pd
sys.path.insert(0, str(_Path(__file__).resolve().parent))
from mff_rates import conversion_factor

def parse_cme_table(path="data/raw/cme_treasury_conversion_factors_TCF_2026-10-21.xlsx"):
    d = pd.read_excel(path, "Conversion Factors", header=None)
    rows, contract, months = [], None, None
    for i in range(len(d)):
        r = d.iloc[i].tolist()
        first = str(r[0])
        if "FUTURES" in first.upper():
            u = first.upper()
            contract = ("TN" if "ULTRA" in u and "10" in u else "UB" if "ULTRA" in u else
                        "TU" if u.startswith("2-YEAR") else "3YR" if u.startswith("3-YEAR") else
                        "FV" if u.startswith("5-YEAR") else "TY" if u.startswith("10-YEAR") else
                        "TWE" if u.startswith("20-YEAR") else "US")
            months = None
            continue
        if "Coupon" in [str(x).strip() for x in r]:
            months = {j: pd.Timestamp(v) for j, v in enumerate(r) if hasattr(v, "year")}
            continue
        if months and isinstance(r[5], str) and re.fullmatch(r"912[0-9A-Z]{6}", r[5]):
            for j, m in months.items():
                v = r[j]
                if isinstance(v, (int, float)) and not pd.isna(v):
                    rows.append(dict(contract=contract, coupon=float(r[2]), issue=pd.Timestamp(r[3]),
                                     maturity=pd.Timestamp(r[4]), cusip=r[5], delivery=m, cme_cf=float(v)))
    return pd.DataFrame(rows)

if __name__ == "__main__":
    t = parse_cme_table()
    t["our_cf"] = [conversion_factor(r.coupon, r.maturity, r.delivery, r.contract) for r in t.itertuples()]
    t["diff"] = (t["our_cf"] - t["cme_cf"]).round(4)
    print("contracts:", t.groupby("contract").size().to_dict())
    print("rows:", len(t), " exact matches:", int((t["diff"] == 0).sum()), " max |diff|:", t["diff"].abs().max())
    print(t[t["diff"] != 0].head(20).to_string())
    t.to_csv("data/derived/cf_validation_vs_cme.csv", index=False)
