#pragma once
#include <cstddef>
#include <span>
#include <utility>

namespace kvant::stats {
struct Moments {
    std::size_t n{};
    double mean{};
    double sample_variance{};
    double sample_stddev{};
    double skewness{};        // Fisher-Pearson bias-corrected sample skewness
    double excess_kurtosis{}; // bias-corrected Fisher excess kurtosis
};

[[nodiscard]] Moments moments(std::span<const double> x);
[[nodiscard]] double mean(std::span<const double> x);
[[nodiscard]] double sample_variance(std::span<const double> x);
[[nodiscard]] double sample_covariance(std::span<const double> x,
                                       std::span<const double> y);
} // namespace kvant::stats
