#pragma once
#include <cstddef>
namespace kvant::monitoring {
struct DeflatedSharpeResult{bool required{};double expected_max_sharpe{},test_statistic{},probability{};};
[[nodiscard]]DeflatedSharpeResult automatic_deflated_sharpe(double observed_sharpe,double sharpe_variance,std::size_t tested_variants,double skewness,double excess_kurtosis,std::size_t observations);
[[nodiscard]]bool require_deflated_sharpe(std::size_t tested_variants)noexcept;
}
