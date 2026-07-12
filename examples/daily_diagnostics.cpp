#include "kvant/stats/descriptive.hpp"
#include "kvant/stats/diagnostics.hpp"
#include "kvant/stats/distributions.hpp"
#include "kvant/stats/stationarity.hpp"
#include <iostream>
#include <vector>
int main(){using namespace kvant::stats;std::vector<double>returns{.01,-.005,.012,.003,-.008,.004,.006,-.002,.009,-.004,.007,.002};auto m=moments(returns);auto ci=mean_confidence_interval(returns);auto jb=jarque_bera(returns);auto lb=ljung_box(returns,3);auto adf=augmented_dickey_fuller(returns);auto ks=kpss(returns);std::cout<<"n="<<m.n<<" mean="<<m.mean<<" vol="<<m.sample_stddev<<" skew="<<m.skewness<<" excess_kurtosis="<<m.excess_kurtosis<<'\n'<<"95% mean CI=["<<ci.first<<", "<<ci.second<<"]\n"<<"JB p="<<jb.p_value<<" LB p="<<lb.p_value<<" DW="<<durbin_watson(returns)<<'\n'<<"ADF statistic="<<adf.statistic<<" reject unit root="<<adf.reject_at_5_percent<<'\n'<<"KPSS statistic="<<ks.statistic<<" reject stationarity="<<ks.reject_at_5_percent<<'\n';}
