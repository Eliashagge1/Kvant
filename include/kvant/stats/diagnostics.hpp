#pragma once
#include <cstddef>
#include <span>
#include <vector>

namespace kvant::stats {
struct TestResult {
    double statistic{};
    double p_value{};
    bool reject{};
};

[[nodiscard]] std::vector<double> autocorrelations(std::span<const double> x,
                                                   std::size_t max_lag);
[[nodiscard]] TestResult ljung_box(std::span<const double> residuals,
                                   std::size_t lags,
                                   std::size_t fitted_parameters = 0,
                                   double alpha = 0.05);
[[nodiscard]] TestResult jarque_bera(std::span<const double> x,
                                    double alpha = 0.05);
[[nodiscard]] double durbin_watson(std::span<const double> residuals);
} // namespace kvant::stats
