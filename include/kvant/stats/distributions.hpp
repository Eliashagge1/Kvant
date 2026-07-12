#pragma once
#include <cstddef>
#include <span>
#include <utility>

namespace kvant::stats {
[[nodiscard]] double normal_pdf(double x, double mu = 0.0, double sigma = 1.0);
[[nodiscard]] double normal_cdf(double x, double mu = 0.0, double sigma = 1.0);
[[nodiscard]] double student_t_pdf(double x, double degrees_of_freedom);
[[nodiscard]] double student_t_cdf(double x, double degrees_of_freedom);
[[nodiscard]] double student_t_quantile(double probability, double degrees_of_freedom);

// Returns [lower, upper] for an unknown mean and unknown variance.
[[nodiscard]] std::pair<double, double> mean_confidence_interval(
    std::span<const double> x, double confidence = 0.95);

// Stable two-hypothesis Bayes update. prior and likelihoods must be in [0,1].
[[nodiscard]] double bayes_update(double prior_probability,
                                  double likelihood_if_true,
                                  double likelihood_if_false);

[[nodiscard]] double bonferroni_alpha(double family_alpha, std::size_t tests);
[[nodiscard]] double bonferroni_adjusted_p(double p_value, std::size_t tests);
} // namespace kvant::stats
