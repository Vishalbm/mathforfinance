# Data snapshot

Raw files exactly as downloaded on 25 October 2026 (cleaned only by dropping columns/rows noted below). Everything in `derived/` is produced from these by the code in `articles/`.

| File | What it is | Source |
|---|---|---|
| `raw/treasury_par_yield_curve_2021.csv` … `_2023.csv` | Daily Treasury par yield curve rates | [US Treasury, Daily Treasury Par Yield Curve Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2023) |
| `raw/fed_gsw_nominal_curve_2021_2023H1.csv` | Fed staff fitted nominal curve (Svensson parameters and zero yields `SVENY01`–`SVENY10`), Jan 2021–Jun 2023 rows only | [Federal Reserve Board, Gürkaynak, Sack and Wright (2007) yield curve tables](https://www.federalreserve.gov/data/yield-curve-tables/feds200628_1.html) |
| `raw/nyfed_sofr_2023.csv`, `raw/nyfed_tgcr_2023.csv` | SOFR and Tri-Party General Collateral Rate | [New York Fed Markets Data API](https://markets.newyorkfed.org/static/docs/markets-api.html) |
| `raw/fedinvest_prices_2023-01.csv` … `-03.csv` | End-of-day prices for every marketable Treasury note and bond (bills, TIPS and FRNs removed) | [TreasuryDirect FedInvest historical prices](https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate) |
| `raw/treasurydirect_auctions_notes_bonds_2010_2023Q1.csv` | Auction records: CUSIP, original term, issue/dated/maturity dates, coupon | [TreasuryDirect securities API](https://www.treasurydirect.gov/webapis/webapisecurities.htm) |
| `raw/cme_treasury_conversion_factors_TCF_2026-10-21.xlsx` | CME's published conversion factors and deliverable securities for currently listed Treasury futures (used to test our formula and basket rules) | [CME Group, Treasury Conversion Factors](https://www.cmegroup.com/trading/interest-rates/treasury-conversion-factors.html) |
| `raw/yahoo_ZT/ZF/ZN_front_continuous_2023Q1.csv` | Daily closes of the front 2y/5y/10y Treasury futures. Third-party data, used **only as a check** on our futures model | Yahoo Finance chart data |

Notes
- FedInvest prices are clean prices per 100 face. We use the `end_of_day` column.
- CME's full historical settlement prices are a paid product, so the analysis values futures from the cheapest-to-deliver bond and repo instead; the Yahoo series is there to show how close that gets.
