1. Probability & Statistics

Unbiased sample variance: s² = Σ(xᵢ - x̄)² / (n-1) — Bessel's correction, used throughout for volatility/error estimates
Skewness (3rd standardized moment) and excess kurtosis (4th standardized moment − 3) — quantifying fat tails in return distributions
Student's t-distribution vs. Normal — degrees-of-freedom parameter controls tail thickness; used instead of Normal when modeling returns
Bayes' theorem: P(A|B) = P(B|A)P(A) / P(B) — combining independent signals, updating regime probability
Augmented Dickey-Fuller (ADF) test — specific unit-root/stationarity test (null: series has a unit root / is non-stationary)
KPSS test — complementary stationarity test (null: series is stationary) — run alongside ADF since they test opposite nulls
Ljung-Box Q-statistic — tests whether a batch of autocorrelations is jointly zero; used on ARIMA/GARCH residuals to confirm the model captured the structure
Jarque-Bera test — normality test using sample skewness and kurtosis
Durbin-Watson statistic — detects autocorrelation in regression residuals
Central Limit Theorem (precise form): x̄ₙ → N(μ, σ²/n) as n→∞ — justifies confidence intervals on aggregated stats
Confidence interval: x̄ ± t*·(s/√n) (t-distribution version for finite samples)
Bonferroni correction (or similar family-wise error correction) — needed once you're testing more than one signal variant, directly relevant to §8.3

2. Linear Algebra

Eigendecomposition: Av = λv — the literal computation behind PCA and factor decomposition
Singular Value Decomposition: A = UΣVᵀ — more numerically stable than eigendecomposition for ill-conditioned data matrices
Cholesky decomposition: A = LLᵀ — requires A positive definite; used to (a) verify/repair a covariance matrix before feeding it to OSQP, (b) simulate correlated random variables for Monte Carlo
QR decomposition: A = QR — the numerically stable way Eigen should solve least-squares regression, preferred over direct normal equations when X is ill-conditioned
Normal equations: β = (XᵀX)⁻¹XᵀY — closed-form OLS, fine when X is well-conditioned
Condition number κ(A) = σ_max/σ_min — diagnoses whether a covariance matrix is near-singular before optimization
Positive semi-definiteness: all eigenvalues ≥ 0 — the exact property a covariance matrix must satisfy or OSQP fails/produces garbage

3. Calculus & Gradient-Based Optimization

Gradient: ∇f(θ) — vector of partial derivatives, the object every training loop computes
Chain rule: ∂z/∂x = (∂z/∂y)(∂y/∂x) — literally what backpropagation is
Gradient descent update: θₜ₊₁ = θₜ − η∇L(θₜ)
Adam optimizer — momentum + per-parameter adaptive learning rate (m̂, v̂ bias-corrected moment estimates); the near-default optimizer for the PyTorch training loop, worth knowing the actual update rule rather than treating it as a black box
Lagrangian: L(x,λ) = f(x) + λᵀg(x) — the bridge from constrained to unconstrained optimization
KKT conditions (stationarity, primal feasibility, dual feasibility, complementary slackness) — the theoretical conditions OSQP's solution must satisfy at optimality
Convexity test: f(θx+(1−θ)y) ≤ θf(x)+(1−θ)f(y), or equivalently Hessian ∇²f ⪰ 0 — determines whether Markowitz mean-variance is a well-posed QP (it is, as long as Σ is PSD)

4. Time-Series Econometrics (the deepest section — this is where most of the modeling risk lives)

AR(p): Xₜ = c + Σφᵢ Xₜ₋ᵢ + εₜ
MA(q): Xₜ = μ + Σθᵢ εₜ₋ᵢ + εₜ
ARIMA(p,d,q) — d is the differencing order applied to induce stationarity before fitting AR/MA terms
ACF/PACF-based order selection — PACF cuts off sharply at lag p for a pure AR(p) process; ACF cuts off at lag q for a pure MA(q) process — this is the actual diagnostic procedure for picking p and q, not just "look at autocorrelation"
GARCH(1,1): σ²ₜ = ω + α·ε²ₜ₋₁ + β·σ²ₜ₋₁ — the standard volatility-clustering model
EGARCH / GJR-GARCH — asymmetric extensions capturing the leverage effect (volatility rises more after negative returns than positive ones of the same size)
Maximum Likelihood Estimation — the actual fitting method behind statsmodels/arch for both ARIMA and GARCH parameters (and what Ceres Solver's nonlinear least-squares would be approximating if hand-rolled)
Hidden Markov Model — transition matrix P(sₜ|sₜ₋₁), emission distributions P(xₜ|sₜ), fit via Baum-Welch (an EM algorithm instance), most-likely state path via the Viterbi algorithm
Kalman filter, explicit recursion:

Predict: x̂ₜ|ₜ₋₁ = Fx̂ₜ₋₁, Pₜ|ₜ₋₁ = FPₜ₋₁Fᵀ + Q
Update: Kₜ = Pₜ|ₜ₋₁Hᵀ(HPₜ|ₜ₋₁Hᵀ + R)⁻¹, x̂ₜ = x̂ₜ|ₜ₋₁ + Kₜ(zₜ − Hx̂ₜ|ₜ₋₁)
This is literally the "online update" mechanism in §6, not just a modeling tool


Random walk / weak-form Efficient Market Hypothesis — the specific null model every signal must beat to be worth deploying
Engle-Granger two-step test and Johansen test — cointegration tests, only needed if a pairs/mean-reversion signal is added later

5. Optimization (Portfolio Layer)

QP standard form: minimize ½xᵀPx + qᵀx, subject to l ≤ Ax ≤ u — the exact shape OSQP expects, and the shape §8.4's code block builds
Markowitz mean-variance: minimize wᵀΣw − λμᵀw, subject to Σwᵢ = 1 (and bound/sector constraints) — maps P = Σ (covariance), q = −μ + turnover-cost vector
Efficient frontier — the set of (risk, return) pairs traced by varying λ; useful for sanity-checking the optimizer's output makes sense
ADMM (Alternating Direction Method of Multipliers) — the specific algorithm OSQP runs internally; understanding it explains OSQP's convergence tolerances and warm-start behavior
Gauss-Newton / Levenberg-Marquardt — the specific nonlinear least-squares algorithms underlying Ceres Solver, if you hand-roll GARCH/ARIMA MLE fitting in C++

6. Machine Learning Math

MSE: (1/n)Σ(yᵢ−ŷᵢ)², MAE: (1/n)Σ|yᵢ−ŷᵢ| — regression loss choices (MAE is more robust to return outliers)
Cross-entropy: −Σyᵢlog(ŷᵢ) — for direction-classification-style targets
L1 (Lasso) / L2 (Ridge) penalty added to the loss — λΣ|wᵢ| or λΣwᵢ² — controls overfitting in the simpler linear/tree models
Bias-variance decomposition: Total Error = Bias² + Variance + Irreducible Error — the theoretical reason a model can fit training data well and still fail out-of-sample
Gini impurity / information gain (entropy reduction) — the actual split criteria inside XGBoost/LightGBM trees
Gradient boosting: Fₘ(x) = Fₘ₋₁(x) + γₘhₘ(x), where hₘ is fit to the negative gradient of the loss w.r.t. Fₘ₋₁ — the precise mechanism, not just "trees added sequentially"
Reverse-mode automatic differentiation — what PyTorch's .backward() actually implements; chain rule applied over the computational graph in reverse topological order
Shapley value: φᵢ = Σ_{S⊆N{i}} [|S|!(n−|S|−1)!/n!]·[v(S∪{i}) − v(S)] — the exact game-theoretic formula SHAP approximates

7. Quant Finance Metrics (exact formulas)

Sharpe ratio: SR = (R_p − R_f) / σ_p
Deflated Sharpe Ratio (Bailey & López de Prado) — adjusts the observed Sharpe for the number of trials/variants tested and for non-normal skew/kurtosis in returns; this is the specific correction that makes §8.3's "apply DSR after more than one variant" concrete rather than hand-wavy
Probabilistic Sharpe Ratio (PSR) — probability that the true Sharpe exceeds a benchmark, given the observed Sharpe and sample size
Information Coefficient — Pearson or (more robust) Spearman rank correlation between predicted and realized returns
Information Ratio: IR = active return / tracking error
Grinold's Fundamental Law: IR ≈ IC × √Breadth
CAPM: Rᵢ = R_f + βᵢ(R_m − R_f) — the baseline decomposition alpha/beta reporting is built on
Multi-factor regression (Fama-French-style) — Rᵢ = α + Σβₖ·Fₖ + ε, for factor-exposure prediction
Brier score: (1/N)Σ(fₜ − oₜ)² — calibration metric for probabilistic forecasts
Value at Risk (historical simulation, parametric/variance-covariance, or Monte Carlo method) and Conditional VaR / Expected Shortfall (mean loss beyond the VaR threshold)
Maximum drawdown: max over t of (peak value up to t − value at t) / peak value up to t
Square-root market impact model: cost ≈ σ · sign(order) · (|order| / ADV)^0.5 — the specific functional form to implement in both the backtester fills and the OSQP cost term
Kelly criterion: f* = μ/σ² (continuous approximation) — only if position sizing moves beyond mean-variance weights

8. Statistical Process Control (Drift Detection)

CUSUM: Sₜ = max(0, Sₜ₋₁ + (xₜ − target − k)) — general cumulative-deviation control chart
Page-Hinkley test, exact recursion (already in the C++ snippet in §6): running mean update, cumulative sum minus mean minus tolerance δ, flag when (cumulative − min_cumulative) > λ — worth understanding the δ/λ tradeoff explicitly: δ controls sensitivity to small drifts, λ controls false-alarm rate
EWMA: Sₜ = α·xₜ + (1−α)·Sₜ₋₁ — used both as an alternative drift detector and as the ensemble-reweighting mechanism after confirmed drift

9. Resampling & Cross-Validation

Bootstrap resampling — sampling with replacement to build an empirical distribution of a statistic (e.g., Sharpe ratio confidence interval)
Block bootstrap — resamples contiguous blocks rather than iid points, necessary specifically because return series are autocorrelated (plain iid bootstrap understates the true variance)
Purged K-fold cross-validation (López de Prado) — removes training samples whose label window overlaps the test window, preventing leakage from overlapping-horizon labels
Embargo — an additional buffer period after the test set excluded from training, guarding against serial correlation leaking information backward
Combinatorial Purged Cross-Validation (CPCV) — generates multiple train/test path combinations from N groups, producing a distribution of backtest paths instead of one

10. Stochastic Calculus (optional — derivatives only)

Geometric Brownian Motion: dS = μS dt + σS dW
Itô's lemma: df = (∂f/∂t + μS ∂f/∂S + ½σ²S² ∂²f/∂S²)dt + σS ∂f/∂S dW — the derivation tool behind Black-Scholes
Black-Scholes PDE and closed-form formula — what QuantLib implements for option pricing
Risk-neutral valuation / martingale pricing — the theoretical justification for using the risk-free rate as the discount rate under the risk-neutral measure
