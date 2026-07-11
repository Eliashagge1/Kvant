# Kvant

**Scope:** A daily quantitative analysis engine, built on your own math models + ML, that predicts market outcomes, checks itself against reality every day, and adjusts in a disciplined way instead of chasing noise. **This version reworks the stack so the runtime engine is written in C++, with Python + PyTorch used only where it's genuinely the easier tool: model training.**

**Design philosophy, unchanged:** this is a systems-design problem wearing a math costume. Every section below exists to protect the discipline that keeps the system honest, regardless of language.

---
## 1. The Language Split — What's C++, What Stays Python

| Stays in Python (offline, not latency-critical) | Lives in C++ (the runtime engine) |
| --- | --- |
| Model training — PyTorch for neural nets, scikit-learn/XGBoost/LightGBM for everything else | Data ingestion & point-in-time store |
| Hyperparameter search, experimentation, new-signal research | Feature computation for live daily inference |
| SHAP explainability analysis (run periodically as a diagnostic, not in the live loop) | Risk model & portfolio optimizer |
| Fitting ARIMA/GARCH/HMM parameters (recommended default — see §4) | Backtester |
|  | Execution / paper-trading logic |
|  | Self-correction loop control logic (drift detection, shadow-mode gating, ensemble reweighting, Kalman filter online updates) |
|  | Model **inference** (loading the trained artifact and running it) |

**The bridge is a portable, Python-free artifact**, not a live Python process:

- **Neural nets:** train in PyTorch, export with `torch.jit.script()` / `torch.jit.trace()` to **TorchScript**, then load and run it in C++ with **LibTorch** — no Python interpreter in production.

```python
# Python — training side
scripted = torch.jit.script(model)
scripted.save("model.pt")
```

```cpp
// C++ — inference side (LibTorch)
torch::jit::script::Module model = torch::jit::load("model.pt");
auto output = model.forward({input_tensor}).toTensor();
```

- **Gradient-boosted trees (XGBoost/LightGBM):** train in Python as usual, then compile the trained ensemble into standalone C code with **Treelite** (the model-exchange format) and **TL2cgen** (the compiler) — the result is a dependency-free shared library your C++ core calls directly, with no XGBoost/LightGBM runtime needed in production either.

This pattern — train anywhere, compile/export to a native artifact, run inference in the C++ core — is what gives you "everything in C++ except ML" without actually writing gradient boosting or backprop by hand in C++.

**New failure mode this introduces — training/serving skew:** if the C++ feature-computation code doesn't compute features *exactly* the way the Python training pipeline did, the model receives subtly wrong inputs and predictions degrade silently — the classic "it worked in training" bug. Mitigation: define every feature transform once, in a shared spec (a JSON/YAML config both sides read, or at minimum a fixed set of golden-file test cases with known inputs/outputs), and add a CI check that asserts the Python and C++ feature pipelines produce identical values on the same fixed sample data. Treat any drift here as a build-breaking bug, not a known quirk.

---

## 2. System Architecture

```
                                   ┌─────────────────────────────┐
                                   │  PYTHON (offline, research)  │
                                   │  training loops, hyperparam  │
                                   │  search, SHAP, signal R&D    │
                                   └───────────────┬──────────────┘
                                                    │ export: TorchScript (.pt)
                                                    │         Treelite/TL2cgen (.so)
                                                    ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌────────────────┐     ┌───────────┐
│ DATA LAYER  │ --> │ FEATURE /    │ --> │ PREDICTION     │ --> │ RISK & PORTFOLIO│ --> │ EXECUTION │
│ (DuckDB PIT │     │ ALPHA LAYER  │     │ MODELS         │     │ CONSTRUCTION    │     │ (paper/   │
│ store, C++) │     │ (C++)        │     │ (LibTorch /    │     │ (Eigen + OSQP,  │     │  live)    │
│             │     │              │     │  Treelite, C++)│     │  C++)           │     │  C++      │
└─────────────┘     └──────────────┘     └───────────────┘     └────────────────┘     └───────────┘
                                                  │                                          │
                                                  ▼                                          ▼
                                        ┌───────────────────────────────────────────────────────┐
                                        │   DIAGNOSTICS & SELF-CORRECTION LOOP  (C++)            │
                                        │   Predict → Wait → Resolve → Diagnose → Adjust         │
                                        │   feeds back into Feature Layer & Prediction Models    │
                                        │   only on confirmed drift, never on a single miss      │
                                        └───────────────────────────────────────────────────────┘
```

Everything below the dashed Python box is a single C++ process (or a small set of them). The only thing crossing the boundary is a file on disk — a `.pt` TorchScript model or a Treelite-compiled `.so` — never a live RPC call into a Python process. That keeps production dependency-free and keeps the research side free to be as messy and iterative as it needs to be.

---

## 3. Data Layer (C++)

### 3.1 What you still need to collect

Unchanged from the language-agnostic version — market data (OHLCV), corporate actions, fundamentals, macro, optionally alternative data. What changes is *how you get it and store it* in a C++-first stack.

### 3.2 The yfinance problem in C++

yfinance is a Python library that scrapes Yahoo's internal endpoints — there is no native C++ port, and reverse-implementing that scraping logic in C++ just means maintaining your own fragile, unofficial client instead of using the community-maintained Python one. Two honest options:

- **Bridge script (keeps yfinance around during prototyping):** a small, separate Python script runs yfinance on a schedule and writes each day's bars to Parquet/CSV. Your C++ engine never imports yfinance or talks to Python at runtime — it just reads the file. DuckDB can query Parquet/CSV directly, so this is a clean, thin seam.
- **Skip straight to a REST vendor (cleaner for a mostly-C++ system):** Alpha Vantage, Twelve Data, Polygon.io, or Financial Modeling Prep are plain HTTP + JSON APIs — a much more natural fit for C++ than reverse-engineering Yahoo's endpoints. Call them with **cpr** (a friendly libcurl wrapper) and parse responses with **nlohmann/json**. Given the rest of this rework is already accepting more upfront setup cost for a cleaner long-term system, this is the option I'd default to.

### 3.3 Point-in-time store: DuckDB

**DuckDB** is the right fit here — it's an embedded (no server) analytical database, written in C++, with a **native `ASOF JOIN`** that does exactly what you need for point-in-time correctness: attach the most recent *prior* row from one table onto another, in SQL, instead of hand-writing merge logic.

```sql
-- Attach the most recent fundamentals row that was PUBLICLY AVAILABLE
-- as of each price date — this is the look-ahead-bias fix, as one SQL statement.
SELECT p.ticker, p.date, f.*
FROM prices p
ASOF JOIN fundamentals f
  ON p.ticker = f.ticker AND p.date >= f.available_date;
```

One caveat worth knowing: DuckDB's documentation explicitly marks its **C++ API as internal and not guaranteed stable across versions** — it recommends the **C API** for applications that need long-term stability. Practical takeaway: either pin your DuckDB version deliberately, or write your integration against the C API if you want it to survive DuckDB upgrades untouched.

### 3.4 Supporting tools

- **Apache Arrow (C++ core library)** — columnar in-memory format; useful if you ever need to move data efficiently between your C++ engine and a Python research notebook without round-tripping through CSV.
- **cpr + nlohmann/json** — HTTP client and JSON parsing for any REST vendor.
- **Cache aggressively**, same rule as before: a daily engine needs one new bar per ticker per day. Store everything locally in DuckDB; don't re-hit any API for history after the initial bootstrap.

---

## 4. Mathematical Foundations Map (C++ tooling)

| Category | C++ tooling | Notes |
| --- | --- | --- |
| **Statistics & probability** | **Boost.Math** (distributions, special functions), **Eigen** (regression via normal equations / QR) | Solid, mature, no real gap vs. Python here |
| **Linear algebra** | **Eigen** (the standard, header-only) or **Armadillo** (more numpy/Matlab-like syntax if that's an easier mental model) | Covariance matrices, PCA, factor decomposition all live here |
| **Time-series econometrics** | **Recommended default:** fit ARIMA/GARCH/HMM parameters in Python (`statsmodels`/`arch`) as a periodic offline job, and feed the fitted coefficients into the C++ runtime as static/refreshed parameters — the same export pattern as the ML models. **Alternative:** hand-roll in C++ with **Eigen** for the linear algebra and **Ceres Solver** (Google's nonlinear least-squares library) for the MLE fitting step — fully doable, just more assembly required than calling `statsmodels.tsa.ARIMA()`. Kalman filters specifically are simple enough to hand-roll in either case — it's just matrix recursion. | This is the biggest real tooling gap vs. Python. Pick one path deliberately rather than discovering it mid-build. |
| **Optimization theory** | **OSQP** (the QP solver itself, written in C) via **osqp-cpp** (Google's Eigen-based C++ wrapper) for Markowitz-style mean-variance optimization with real-world constraints | This is genuinely a clean swap — cvxpy itself calls OSQP under the hood for QP problems, so you're using the same solver, just directly |
| **Stochastic calculus** | **QuantLib** — the closest thing to institutional-grade quant tooling that exists in open-source C++: derivatives pricing, curve construction, day-count conventions, no-arbitrage models | Only relevant if you touch options/derivatives. Skip entirely for equity/futures direction-and-sizing work. Better C++ tooling here than almost anywhere else in this table. |
| **ML-specific math** | Handled by the training-side Python tools (§1); the C++ side only needs **LibTorch** (NN inference) and a **Treelite/TL2cgen**-compiled `.so` (tree inference) |  |
| **General-purpose fallback** | **dlib** — a broad C++ toolkit with statistics, general optimization, and some ML utilities bundled together | Worth knowing about if you want fewer separate dependencies, at the cost of using its specific API conventions |

The **Fundamental Law of Active Management** (Information Ratio ≈ Information Coefficient × √Breadth) is math, not code — it applies unchanged regardless of language, and it's still the first test to run on any new signal.

---

## 5. What The Engine Predicts

Unchanged — this is a modeling question, not a language question:

1. Return direction and magnitude, by horizon
2. Volatility
3. Correlation/covariance structure
4. Regime state
5. Transaction costs / market impact / liquidity
6. Factor exposures

---

## 6. The Daily Self-Correcting Loop (C++)

```
  ┌─────────┐    ┌──────┐    ┌─────────┐    ┌──────────┐    ┌────────┐
  │ PREDICT │ -> │ WAIT │ -> │ RESOLVE │ -> │ DIAGNOSE │ -> │ ADJUST │ -┐
  └─────────┘    └──────┘    └─────────┘    └──────────┘    └────────┘  │
       ▲                                                                │
       └────────────────────────────────────────────────────────────────┘
```

**Predict** — run inference through LibTorch (`model.forward()`) or the Treelite/TL2cgen `.so`, log the prediction, confidence interval, feature snapshot, and model version to DuckDB.

**Wait** — no code change from the original plan; this step is a discipline, not a library.

**Resolve** — ingest the actual outcome via the same point-in-time DuckDB pipeline.

**Diagnose** — this is where hand-rolling in C++ is actually *no loss at all*: CUSUM and Page-Hinkley are a few dozen lines of arithmetic, not a library dependency.

```cpp
class PageHinkley {
public:
    void update(double error) {
        mean_ += (error - mean_) / ++n_;
        cumulative_ += error - mean_ - delta_;
        min_cumulative_ = std::min(min_cumulative_, cumulative_);
        drift_detected = (cumulative_ - min_cumulative_) > lambda_;
    }
    bool drift_detected = false;
private:
    double mean_ = 0, cumulative_ = 0, min_cumulative_ = 0;
    double delta_ = 0.005, lambda_ = 50.0;  // tune to your error scale
    int n_ = 0;
};
```

(SHAP-based error attribution stays on the Python side as a periodic offline diagnostic — it's not latency-critical, so there's no reason to port it.)

**Adjust** — the three tiers from the original plan, in C++ terms:

- **Online/incremental update** — a Kalman filter update is pure Eigen matrix algebra; no library needed beyond Eigen itself.
- **Ensemble reweighting** — a small amount of arithmetic (exponential/multiplicative weighting); trivial in C++.
- **Full retrain** — this one **does** cross back into Python: trigger a retraining job, get a new exported artifact (TorchScript or Treelite `.so`), and promote it through shadow mode exactly as before.

**Shadow-mode gate** — unchanged: any updated model runs in parallel without controlling live decisions for a validation window before promotion. This is a code-level gate (a boolean flag + a logged comparison window), not a library concern.

---

## 7. Validation & Backtesting Discipline

The concepts are unchanged (purged/embargoed CV, CPCV, IC testing, realistic transaction costs, alpha decay tracking) — what changes is tooling availability:

- **`mlfinlab`style purged/embargoed CV and CPCV have no C++ package equivalent.** These are index-bookkeeping algorithms (generating train/test splits with purge windows), not numerically heavy — entirely feasible to hand-implement in C++ with `std::vector` and some date arithmetic, just budget the time to write and test it carefully, since a bug here silently reintroduces the exact leakage it's supposed to prevent.
- **Deflated Sharpe Ratio** — a formula, not a library call, in either language.
- **Transaction cost realism** — bake it into the C++ backtester's fill logic directly (spread + commission + a square-root market-impact term scaled by order size / ADV), same principle as before, now living in the optimizer's objective via OSQP rather than cvxpy.

---

## 8. Common Failure Modes — Checklist & C++-Specific Mitigations

### 8.1 Look-ahead bias

Use DuckDB's `ASOF JOIN` (§3.3) as the structural fix — it makes pulling a future row for a past date syntactically awkward rather than an easy mistake. Store `period_end_date` and `available_date` separately on every fundamentals row, always join on `available_date` with a small safety lag.

### 8.2 Survivorship bias

Same as before — low risk on a hand-picked single ticker, becomes a data-source problem (Norgate/Sharadar) the moment you screen a wider universe. Build universe membership per historical date, not from today's index composition.

### 8.3 Overfitting via repeated test-set peeking

Log every experiment run to an append-only DuckDB table (params, code/git commit hash, metrics) — this is easier in C++ than it sounds, since you're already using DuckDB for everything else. Apply the Deflated Sharpe Ratio once you've tried more than one variant.

### 8.4 Transaction-cost blindness

Put the turnover penalty directly in the OSQP objective, not as a post-hoc filter:

```cpp
// Illustrative — osqp-cpp's exact API surface may differ slightly by version
Eigen::SparseMatrix<double> P = covariance_matrix;              // risk term
Eigen::VectorXd q = -expected_returns + turnover_cost_vector;   // return - cost
OsqpInstance instance;
instance.objective_matrix = P;
instance.objective_vector = q;
instance.constraint_matrix = constraint_matrix;   // sector caps, leverage, etc.
instance.lower_bounds = lb;
instance.upper_bounds = ub;
OsqpSolver solver;
solver.Init(instance, OsqpSettings());
solver.Solve();
```

Deliberately bias cost assumptions high in the backtester's fill logic.

### 8.5 Treating one backtest run as proof

Report the distribution from your hand-rolled CPCV (§7), not a single number. Bootstrap-resample trade-level returns for a confidence interval.

### 8.6 Reacting to every miss instead of confirmed drift

The `PageHinkley` class in §6 *is* the fix — route every error through it, and only call the adjust function when `drift_detected` flips true. Enforce a hard-coded cooldown (minimum N days between adjustments) in the same control loop.

### 8.7 Point-in-time violations in fundamentals

Structurally the same bug as 8.1 — same `available_date` + lag-buffer join, same DuckDB `ASOF JOIN` fix. Never use a data source's "current" fundamentals snapshot for historical backtesting.

### 8.8 Training/serving skew (new in this version)

Covered in §1 — the risk introduced specifically by splitting training (Python) from inference (C++). Mitigation: one shared feature-transform spec, golden-file parity tests, and a CI check that fails the build if Python and C++ feature outputs diverge on fixed sample data.

---

## 9. Tech Stack

| Layer | Tooling |
| --- | --- |
| **Training (Python, offline)** | PyTorch (neural nets), scikit-learn / XGBoost / LightGBM (everything else), `statsmodels`/`arch` (ARIMA/GARCH fitting, if using the recommended default from §4), SHAP (explainability) |
| **Model export/bridge** | `torch.jit.script`/`trace` → TorchScript (`.pt`); Treelite + TL2cgen → compiled `.so` |
| **Data & point-in-time store (C++)** | DuckDB (embedded, native `ASOF JOIN`) |
| **HTTP/data ingestion (C++)** | cpr (HTTP), nlohmann/json (parsing) |
| **Linear algebra (C++)** | Eigen (or Armadillo) |
| **Statistics (C++)** | Boost.Math |
| **Time-series econometrics (C++)** | Eigen + Ceres Solver (if hand-rolling instead of the Python-fit default) |
| **Optimization (C++)** | OSQP via osqp-cpp |
| **Derivatives/stochastic calculus (C++, optional)** | QuantLib |
| **ML inference (C++)** | LibTorch (neural nets), Treelite/TL2cgen-compiled `.so` (trees) |
| **Drift detection (C++)** | Hand-rolled CUSUM/Page-Hinkley (no library needed) |
| **Package management (C++)** | vcpkg or Conan — set this up in Phase 0, not as an afterthought |

---

## 10. Phased Build Roadmap

| Phase | Goal | Exit criterion |
| --- | --- | --- |
| **0 — Setup** | vcpkg/Conan configured; Eigen, DuckDB, cpr, nlohmann/json, OSQP pulled in; repo skeleton | A trivial C++ program links against all five without manual build hacking |
| **1 — Data + honest backtester** | DuckDB point-in-time store; data ingestion (bridge script or direct REST vendor, §3.2); backtester with real costs baked in | `ASOF JOIN` query returns correct point-in-time fundamentals on a hand-checked example; buy-and-hold backtest gives a believable, cost-adjusted number |
| **2 — Baseline model** | Train a simple model in Python (linear/tree-based, single asset), export via Treelite/TL2cgen, load and run inference in C++ | C++ inference output matches Python's prediction on the same input to floating-point precision — this is your first training/serving-skew check |
| **3 — Historic bootstrap + calibration baseline** | Walk-forward train in Python using hand-rolled purged CV (§7); establish baseline error distribution in DuckDB | You know what a "normal" miss looks like before going live |
| **4 — Risk & portfolio layer** | Eigen covariance/factor model + OSQP optimizer | Position sizing respects constraints automatically, cost penalty included in the objective |
| **5 — Self-correction loop** | Predict → Wait → Resolve → Diagnose → Adjust, in C++, running in shadow mode | `PageHinkley` correctly flags injected synthetic drift; stays silent on random noise |
| **6 — Paper trading** | Live (no capital) C++ engine, live-vs-backtest divergence tracked in DuckDB | Divergence stays within expected noise bounds |
| **7 — Scale-up (optional)** | Production-grade REST vendor, multi-asset universe, survivorship-bias-free history | No look-ahead or survivorship gaps in the expanded universe |
| **8 — Live capital (optional, small size)** | Deploy with continuous monitoring | Self-correction loop already proven over a full paper-trading cycle |

---

## 11. Success Metrics

Unchanged: Information Coefficient trend, Information Ratio, calibration/Brier score, live-vs-backtest divergence, alpha decay rate. All of these are pure statistics computed from logged predictions and outcomes in DuckDB — no language dependency at all.

---
