#pragma once
#include <cstddef>
#include <span>
#include <string>
#include <vector>
namespace kvant::monitoring {
struct Observation{std::string symbol;long long timestamp{};double prediction{},actual{},probability{},backtest_return{},live_return{};};
struct MetricPoint{long long timestamp{};double value{};std::size_t observations{};};
struct MonitoringSnapshot{double information_coefficient{},information_ratio{},brier_score{},live_backtest_divergence{},alpha_decay_half_life{};std::size_t observations{};};
[[nodiscard]]double pearson_information_coefficient(std::span<const double> predictions,std::span<const double> outcomes);
[[nodiscard]]double information_ratio(std::span<const double> active_returns,double periods_per_year);
[[nodiscard]]double brier_score(std::span<const double> probabilities,std::span<const double> binary_outcomes);
[[nodiscard]]double mean_live_backtest_divergence(std::span<const double> live_returns,std::span<const double> backtest_returns);
[[nodiscard]]double alpha_decay_half_life(std::span<const double> horizon_days,std::span<const double> information_coefficients);
[[nodiscard]]std::vector<MetricPoint> rolling_ic(std::span<const Observation> observations,std::size_t window);
[[nodiscard]]MonitoringSnapshot snapshot(std::span<const Observation> observations,double periods_per_year,std::span<const double> decay_horizons,std::span<const double> decay_ics);
}
