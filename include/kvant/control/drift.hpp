#pragma once
#include <cstddef>
namespace kvant::control {
struct DriftSignal { bool detected{}; double statistic{}; };
class PageHinkley {
public:
 PageHinkley(double delta,double threshold,std::size_t minimum_observations);
 [[nodiscard]] DriftSignal update(double error);
 void reset() noexcept;
private: double delta_,threshold_,mean_{},cumulative_{},minimum_cumulative_{};std::size_t minimum_observations_,count_{};
};
class Cusum {
public:
 Cusum(double reference_value,double threshold,std::size_t minimum_observations);
 [[nodiscard]] DriftSignal update(double standardized_error);
 void reset() noexcept;
private: double reference_,threshold_,positive_{},negative_{};std::size_t minimum_observations_,count_{};
};
}
