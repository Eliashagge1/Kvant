#include "kvant/stats/descriptive.hpp"
#include "kvant/stats/distributions.hpp"
#include "kvant/stats/diagnostics.hpp"
#include "kvant/stats/stationarity.hpp"
#include <cmath>
#include <iostream>
#include <vector>

int failures=0;
void expect(bool ok,const char*msg){if(!ok){std::cerr<<"FAIL: "<<msg<<'\n';++failures;}}
void near(double a,double b,double eps,const char*msg){expect(std::abs(a-b)<=eps,msg);}
int main(){using namespace kvant::stats;
 std::vector<double>x{2,4,4,4,5,5,7,9}; near(mean(x),5,1e-12,"mean");near(sample_variance(x),32.0/7.0,1e-12,"Bessel variance");
 near(normal_cdf(0),.5,1e-14,"normal cdf");near(student_t_cdf(0,5),.5,1e-12,"t cdf");near(student_t_quantile(.975,10),2.22813885,1e-6,"t quantile");
 near(bayes_update(.2,.8,.1),2.0/3.0,1e-12,"Bayes update");near(bonferroni_adjusted_p(.02,10),.2,1e-12,"Bonferroni");
 std::vector<double>e{1,-1,1,-1,1,-1};expect(durbin_watson(e)>3,"Durbin-Watson negative autocorrelation");
 std::vector<double>stationary;for(int i=0;i<120;++i)stationary.push_back(std::sin(i*1.7)+0.1*std::cos(i*.3));auto adf=augmented_dickey_fuller(stationary,1);expect(adf.statistic<0,"ADF statistic");auto ks=kpss(stationary);expect(ks.statistic>=0,"KPSS statistic");
 auto ci=mean_confidence_interval(x);expect(ci.first<5&&ci.second>5,"mean CI");
 if(failures==0)std::cout<<"All tests passed\n";
 return failures==0?0:1;
}
