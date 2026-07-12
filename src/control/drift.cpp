#include "kvant/control/drift.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace kvant::control {
PageHinkley::PageHinkley(double d,double t,std::size_t n):delta_(d),threshold_(t),minimum_observations_(n){if(d<0||t<=0||n<2)throw std::invalid_argument("invalid Page-Hinkley settings");}
DriftSignal PageHinkley::update(double e){if(!std::isfinite(e))throw std::invalid_argument("error must be finite");++count_;mean_+=(e-mean_)/static_cast<double>(count_);cumulative_+=e-mean_-delta_;minimum_cumulative_=std::min(minimum_cumulative_,cumulative_);double s=cumulative_-minimum_cumulative_;return{count_>=minimum_observations_&&s>threshold_,s};}
void PageHinkley::reset()noexcept{mean_=cumulative_=minimum_cumulative_=0;count_=0;}
Cusum::Cusum(double k,double h,std::size_t n):reference_(k),threshold_(h),minimum_observations_(n){if(k<0||h<=0||n<2)throw std::invalid_argument("invalid CUSUM settings");}
DriftSignal Cusum::update(double e){if(!std::isfinite(e))throw std::invalid_argument("error must be finite");++count_;positive_=std::max(0.0,positive_+e-reference_);negative_=std::min(0.0,negative_+e+reference_);double s=std::max(positive_,-negative_);return{count_>=minimum_observations_&&s>threshold_,s};}
void Cusum::reset()noexcept{positive_=negative_=0;count_=0;}
}
