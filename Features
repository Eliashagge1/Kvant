1. Setup / Infrastructure

Package manager configured first — vcpkg or Conan (not an afterthought; do this in Phase 0)
Repo skeleton that links against Eigen, DuckDB, cpr, nlohmann/json, and OSQP without manual build hacking

2. Data Layer

Ingestion mechanism — pick one:

Bridge script: a separate Python process runs yfinance on a schedule, writes bars to Parquet/CSV (C++ never touches Python at runtime)
Direct REST vendor: Alpha Vantage / Twelve Data / Polygon.io / Financial Modeling Prep, called via cpr (HTTP) + nlohmann/json (parsing)


Point-in-time store: DuckDB, using native ASOF JOIN to attach the most recent prior row (e.g., fundamentals) to each price date
Data tables: OHLCV prices, corporate actions, fundamentals (with period_end_date and available_date stored separately), macro data, alternative data (optional)
Universe membership tracked per historical date, not from today's index composition (needed to avoid survivorship bias once you go beyond a single ticker)
Local caching discipline — one new bar per ticker per day; never re-hit an API for history after initial bootstrap
Apache Arrow (C++ core) (optional) — for efficient C++ ↔ Python data transfer without CSV round-trips
Decision: pin your DuckDB version, or integrate against DuckDB's C API (not the C++ API, which isn't stability-guaranteed)

3. Feature / Alpha Layer

C++ feature computation engine for live daily inference
A single shared feature-transform spec (JSON/YAML config both Python and C++ read) — or at minimum a fixed set of golden-file input/output test cases
CI check that fails the build if Python and C++ feature outputs diverge on the same fixed sample data (this is the fix for training/serving skew)

4. Model Training (Python, offline)

PyTorch for neural nets
scikit-learn / XGBoost / LightGBM for everything else
statsmodels / arch for ARIMA/GARCH/HMM parameter fitting (recommended default)
Hyperparameter search / experimentation loop
SHAP for periodic offline explainability (not in the live loop)
Fundamental Law of Active Management check (IC × √Breadth) applied to every new signal before it's trusted

5. Model Export / Bridge (the Python→C++ handoff)

torch.jit.script() / torch.jit.trace() → TorchScript .pt file, for neural nets
Treelite + TL2cgen → compiled, dependency-free .so, for gradient-boosted trees
Fitted ARIMA/GARCH/HMM coefficients exported as static/refreshed parameters (same pattern as the ML exports)
Rule: the only thing crossing the Python/C++ boundary is a file on disk — never a live RPC into a Python process

6. Model Inference (C++)

LibTorch — loads and runs the TorchScript .pt model
Loader for the Treelite/TL2cgen-compiled .so — runs tree-model inference
Consumer for the exported econometric coefficients

7. Risk & Portfolio Construction (C++)

Eigen-based covariance matrix / factor model
OSQP solver via osqp-cpp for mean-variance optimization
Constraints in the objective: sector caps, leverage limits, position bounds
Turnover/transaction-cost penalty built directly into the OSQP objective vector (not a post-hoc filter)

8. Backtester (C++)

Historical simulation engine with realistic fills: spread + commission + square-root market-impact term scaled by order size / ADV
Hand-rolled purged/embargoed cross-validation and CPCV (no C++ library equivalent to mlfinlab exists — this must be built and carefully tested)
Deflated Sharpe Ratio calculation
Bootstrap resampling of trade-level returns for confidence intervals (report a distribution, not a single backtest number)

9. Self-Correction Loop (C++)

Predict: run inference, log prediction, confidence interval, feature snapshot, and model version to DuckDB
Wait: process discipline only, no code
Resolve: ingest actual outcomes through the same point-in-time DuckDB pipeline
Diagnose: drift detection via hand-rolled CUSUM / Page-Hinkley (a small standalone class, no library needed)
Adjust, three tiers:

Online/incremental update — Kalman filter update via Eigen matrix algebra
Ensemble reweighting — exponential/multiplicative weighting
Full retrain — triggers back to the Python training pipeline, produces a new exported artifact


Shadow-mode gate: a boolean flag + logged comparison window before any updated model is allowed to control live decisions
Hard-coded cooldown (minimum N days between adjustments) so the loop reacts to confirmed drift, not single misses

10. Execution / Paper Trading (C++)

Paper-trading engine (no capital) that runs the full pipeline live
Live-vs-backtest divergence logged to DuckDB and monitored against expected noise bounds

11. Math/Stats Tooling (C++)

Eigen (or Armadillo) — linear algebra, covariance, PCA, factor decomposition
Boost.Math — distributions, special functions
Ceres Solver (conditional) — only needed if you hand-roll ARIMA/GARCH MLE fitting in C++ instead of using the Python default
QuantLib (optional) — only needed if you touch options/derivatives; skip for pure equity/futures direction-and-sizing
dlib (optional) — general-purpose fallback if you want fewer separate dependencies

12. Cross-Cutting: Logging, Monitoring, Safeguards

Append-only DuckDB experiment log: parameters, git commit hash, metrics, for every run
Structural look-ahead-bias fix: always join on available_date (with a small safety lag), never on period_end_date
Deflated Sharpe Ratio applied automatically once more than one variant has been tested (guards against overfitting via repeated peeking)
Success-metric tracking, all computed from logged DuckDB predictions/outcomes: Information Coefficient trend, Information Ratio, calibration/Brier score, live-vs-backtest divergence, alpha decay rate

13. Not Yet Required, But On the Roadmap

Survivorship-bias-free data source (Norgate/Sharadar) — only becomes necessary once you move past a single hand-picked ticker to a wider universe (Phase 7)
Production-grade REST vendor at scale (Phase 7)
Live capital deployment monitoring (Phase 8) — only after the self-correction loop has proven itself through a full paper-trading cycle
