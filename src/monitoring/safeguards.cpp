#include "kvant/monitoring/safeguards.hpp"
#include <cmath>
#include <numbers>
#include <stdexcept>
namespace kvant::monitoring {namespace {double cdf(double x){return .5*std::erfc(-x/std::sqrt(2.));}double inv(double p){if(!(p>0&&p<1))throw std::invalid_argument("invalid probability");double l=-9,h=9;for(int i=0;i<120;++i){double m=(l+h)/2;(cdf(m)<p?l:h)=m;}return(l+h)/2;}}
bool require_deflated_sharpe(std::size_t variants)noexcept{return variants>1;}
DeflatedSharpeResult automatic_deflated_sharpe(double sr,double variance,std::size_t variants,double skew,double kurt,std::size_t n){if(!require_deflated_sharpe(variants))return{false,0,0,1};if(variance<=0||n<2)throw std::invalid_argument("invalid Deflated Sharpe inputs");constexpr double gamma=.5772156649015329;double expected=std::sqrt(variance)*((1-gamma)*inv(1-1.0/variants)+gamma*inv(1-1.0/(variants*std::numbers::e)));double radicand=(1-skew*sr+(kurt+2)*sr*sr/4)/(n-1);if(radicand<=0)throw std::domain_error("non-positive Deflated Sharpe variance");double statistic=(sr-expected)/std::sqrt(radicand);return{true,expected,statistic,cdf(statistic)};}
}
