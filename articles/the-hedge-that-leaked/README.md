# The Hedge That Leaked

Code and data for the mathforfinance.com article *The Hedge That Leaked: why a DV01-matched Treasury futures hedge lost money when SVB failed*.

## Reproduce every number

```bash
pip install -r articles/the-hedge-that-leaked/requirements-lock.txt
python articles/the-hedge-that-leaked/src/validate_cf.py   # conversion factors vs CME
python articles/the-hedge-that-leaked/src/experiment.py    # daily hedge experiment, Q1 2023 (~5 min)
python articles/the-hedge-that-leaked/src/figures.py       # charts -> figures/
python articles/the-hedge-that-leaked/src/validation.py    # independent checks -> data/derived/validation_summary.json
```

Or open `the_hedge_that_leaked.ipynb`, which runs the same steps and shows the results.

## What the code does

| File | Purpose |
|---|---|
| `src/mff_rates.py` | Bond cash flows and accrued (QuantLib), CME conversion factors, deliverable-basket rules, Svensson curve fit, key-rate shocks, cheapest-to-deliver futures pricing |
| `src/experiment.py` | Each day of Q1 2023: fit the curve, value TU/FV/TY futures, compute key-rate and PCA risk, set four hedges, measure next-day P&L and decompose it |
| `src/validate_cf.py` | Our conversion factors vs CME's published table |
| `src/validation.py` | All independent checks in one place |
| `src/figures.py` | The article's charts |

## Checks (from `data/derived/validation_summary.json`)

- Conversion factors: 2,194 of 2,194 match CME's published values to 4 decimals.
- Deliverable baskets (TU, FV, TY): our rules select exactly the securities CME lists, no more, no fewer.
- Fitted curve vs the Fed's GSW curve, 62 days: mean absolute gap 1.1bp (2y), 0.8bp (5y), 4.9bp (10y).
- Futures model vs Yahoo front-contract closes, Jan–Feb 2023: mean absolute gap 1.0–1.5/32nds.
- P&L decomposition adds back to the total (largest gap < $0.000001).

## Limitations

Futures are valued without the short's delivery options and with overnight repo held flat to delivery; bond and futures prices are not synchronous; PCA is estimated on par yields and applied to zero-rate key shocks; transaction costs are ignored. See the notebook's last section.
