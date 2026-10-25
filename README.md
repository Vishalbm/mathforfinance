# mathforfinance

Code from the articles on [mathforfinance.com](https://mathforfinance.com), free, open notes on quantitative finance from first principles.

Each file collects the code snippets from one post, in the order they appear. Python files use `# %%` cell markers, so you can run them cell by cell in VS Code or Jupyter. Some snippets rely on variables or data that the post sets up in the text, so read them alongside the article.

## Getting started

```bash
git clone https://github.com/Vishalbm/mathforfinance.git
cd mathforfinance
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The KDB+/q file needs a q installation from [KX](https://kx.com).

## Articles with full data and notebooks

| Article | Folder |
|---|---|
| The Hedge That Leaked: why a DV01-matched Treasury futures hedge lost money when SVB failed | [`articles/the-hedge-that-leaked`](articles/the-hedge-that-leaked) |

These rebuild every number from raw public data saved in [`data/raw`](data/raw) (see [`data/README.md`](data/README.md)).

## Code by track

Files are numbered by the post's position in its track's reading order.

### Mathematical Foundations

| # | Post | Code |
|---|---|---|
| 6 | [Linear Algebra for Portfolios](https://mathforfinance.com/linear-algebra-for-portfolios/) | [`06-linear-algebra-for-portfolios.py`](01-mathematical-foundations/06-linear-algebra-for-portfolios.py) |

### Derivatives Pricing

| # | Post | Code |
|---|---|---|
| 3 | [Brownian Motion](https://mathforfinance.com/brownian-motion/) | [`03-brownian-motion.py`](02-derivatives-pricing/03-brownian-motion.py) |

### Fixed Income & Rates

| # | Post | Code |
|---|---|---|
| 8 | [Minimum-Variance and PCA Hedging with Bond Futures](https://mathforfinance.com/minimum-variance-and-pca-hedging-with-bond-futures/) | [`08-minimum-variance-and-pca-hedging-with-bond-futures.py`](03-fixed-income-rates/08-minimum-variance-and-pca-hedging-with-bond-futures.py) |

### Statistics & Machine Learning

| # | Post | Code |
|---|---|---|
| 5 | [Volatility Modeling with GARCH](https://mathforfinance.com/volatility-modeling-with-garch/) | [`05-volatility-modeling-with-garch.py`](05-statistics-machine-learning/05-volatility-modeling-with-garch.py) |
| 6 | [PCA on the Yield Curve](https://mathforfinance.com/pca-on-the-yield-curve/) | [`06-pca-on-the-yield-curve.py`](05-statistics-machine-learning/06-pca-on-the-yield-curve.py) |
| 7 | [Classification Models for Execution Signals](https://mathforfinance.com/classification-models-for-execution-signals/) | [`07-classification-models-for-execution-signals.py`](05-statistics-machine-learning/07-classification-models-for-execution-signals.py) |
| 8 | [Machine Learning for Return Prediction](https://mathforfinance.com/machine-learning-for-return-prediction/) | [`08-machine-learning-for-return-prediction.py`](05-statistics-machine-learning/08-machine-learning-for-return-prediction.py) |
| 9 | [LSTMs for Financial Time Series](https://mathforfinance.com/lstms-for-financial-time-series/) | [`09-lstms-for-financial-time-series.py`](05-statistics-machine-learning/09-lstms-for-financial-time-series.py) |

### Portfolios & Trading

| # | Post | Code |
|---|---|---|
| 3 | [How to Backtest Without Lying to Yourself](https://mathforfinance.com/how-to-backtest-without-lying-to-yourself/) | [`03-how-to-backtest-without-lying-to-yourself.py`](06-portfolios-trading/03-how-to-backtest-without-lying-to-yourself.py) |

### Numerical Methods & Coding

| # | Post | Code |
|---|---|---|
| 1 | [Python Setup for Quants](https://mathforfinance.com/python-setup-for-quants/) | [`01-python-setup-for-quants.py`](07-numerical-methods-coding/01-python-setup-for-quants.py) |
| 2 | [Getting and Cleaning Market Data](https://mathforfinance.com/getting-and-cleaning-market-data/) | [`02-getting-and-cleaning-market-data.py`](07-numerical-methods-coding/02-getting-and-cleaning-market-data.py) |
| 3 | [KDB+/q and Tickerplant Architecture for Tick Data](https://mathforfinance.com/kdb-q-and-tickerplant-architecture-for-tick-data/) | [`03-kdb-q-and-tickerplant-architecture-for-tick-data.q`](07-numerical-methods-coding/03-kdb-q-and-tickerplant-architecture-for-tick-data.q) |
| 4 | [Pricing Options with a Binomial Tree in Python](https://mathforfinance.com/pricing-options-with-a-binomial-tree-in-python/) | [`04-pricing-options-with-a-binomial-tree-in-python.py`](07-numerical-methods-coding/04-pricing-options-with-a-binomial-tree-in-python.py) |
| 5 | [Monte Carlo Simulation](https://mathforfinance.com/monte-carlo-simulation/) | [`05-monte-carlo-simulation.py`](07-numerical-methods-coding/05-monte-carlo-simulation.py) |
| 6 | [Root Finding and Implied Volatility](https://mathforfinance.com/root-finding-and-implied-volatility/) | [`06-root-finding-and-implied-volatility.py`](07-numerical-methods-coding/06-root-finding-and-implied-volatility.py) |
| 7 | [Calibrating Models to Market Data](https://mathforfinance.com/calibrating-models-to-market-data/) | [`07-calibrating-models-to-market-data.py`](07-numerical-methods-coding/07-calibrating-models-to-market-data.py) |
| 8 | [Fast Code: Vectorization and C++ for Quants](https://mathforfinance.com/fast-code-vectorization-and-c-for-quants/) | [`08-fast-code-vectorization-and-c-for-quants.py`](07-numerical-methods-coding/08-fast-code-vectorization-and-c-for-quants.py) |

## Extra

Code from posts that are not currently published on the site, kept in [`extra/`](extra).

| Track | Post | Code |
|---|---|---|
| Statistics & Machine Learning | Cointegration and Pairs Trading | [`cointegration-and-pairs-trading.py`](extra/05-statistics-machine-learning/cointegration-and-pairs-trading.py) |
| Statistics & Machine Learning | Factor Models: Fama–French and Beyond | [`factor-models-fama-french-and-beyond.py`](extra/05-statistics-machine-learning/factor-models-fama-french-and-beyond.py) |
| Portfolios & Trading | Momentum and Mean-Reversion Strategies | [`momentum-and-mean-reversion-strategies.py`](extra/06-portfolios-trading/momentum-and-mean-reversion-strategies.py) |
| Portfolios & Trading | Risk Parity | [`risk-parity.py`](extra/06-portfolios-trading/risk-parity.py) |
| Numerical Methods & Coding | Finite Difference Methods for PDEs | [`finite-difference-methods-for-pdes.py`](extra/07-numerical-methods-coding/finite-difference-methods-for-pdes.py) |
| Numerical Methods & Coding | Fourier Methods for Option Pricing | [`fourier-methods-for-option-pricing.py`](extra/07-numerical-methods-coding/fourier-methods-for-option-pricing.py) |
| Numerical Methods & Coding | Variance Reduction Tricks | [`variance-reduction-tricks.py`](extra/07-numerical-methods-coding/variance-reduction-tricks.py) |
| Careers & Interview Prep | Coding Interviews for Quants | [`coding-interviews-for-quants.py`](extra/08-careers-interview-prep/coding-interviews-for-quants.py) |
| Careers & Interview Prep | Expected Value Puzzles and Betting Games | [`expected-value-puzzles-and-betting-games.py`](extra/08-careers-interview-prep/expected-value-puzzles-and-betting-games.py) |

## Contributing

Found a bug or have a clearer way to write something? Open an issue or a pull request. Corrections are very welcome.

## License

[MIT](LICENSE). The code is free to use, copy and adapt.
