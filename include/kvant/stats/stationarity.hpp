#pragma once
#include <cstddef>
#include <span>

namespace kvant::stats {
enum class Deterministic { none, constant, constant_and_trend };

struct StationarityResult {
    double statistic{};
    double critical_10{};
    double critical_5{};
    double critical_1{};
    bool reject_at_5_percent{};
    std::size_t observations{};
    std::size_t lags{};
};

// ADF null: unit root. Uses an OLS ADF regression and asymptotic critical values.
[[nodiscard]] StationarityResult augmented_dickey_fuller(
    std::span<const double> x,
    std::size_t lag_count = 0,
    Deterministic deterministic = Deterministic::constant);

// KPSS null: level/trend stationary. Newey-West long-run variance.
[[nodiscard]] StationarityResult kpss(
    std::span<const double> x,
    std::size_t bandwidth = 0,
    Deterministic deterministic = Deterministic::constant);
} // namespace kvant::stats
