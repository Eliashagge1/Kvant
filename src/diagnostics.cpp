#include "kvant/stats/diagnostics.hpp"
#include "kvant/stats/descriptive.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace kvant::stats {
namespace {
double gamma_q(double a,double x){
 if(x<0||a<=0)throw std::invalid_argument("invalid gamma arguments");
 if(x==0)return 1;
 if(x<a+1){double ap=a,sum=1/a,del=sum;for(int n=1;n<500;++n){++ap;del*=x/ap;sum+=del;if(std::abs(del)<std::abs(sum)*1e-14)break;}return 1-sum*std::exp(-x+a*std::log(x)-std::lgamma(a));}
 double b=x+1-a,c=1/1e-300,d=1/b,h=d;for(int i=1;i<500;++i){double an=-i*(i-a);b+=2;d=an*d+b;if(std::abs(d)<1e-300)d=1e-300;c=b+an/c;if(std::abs(c)<1e-300)c=1e-300;d=1/d;double del=d*c;h*=del;if(std::abs(del-1)<1e-14)break;}return std::exp(-x+a*std::log(x)-std::lgamma(a))*h;
}
}
std::vector<double> autocorrelations(std::span<const double>x,std::size_t maxlag){if(x.size()<2||maxlag>=x.size())throw std::invalid_argument("invalid lag");double m=mean(x),den=0;for(double v:x)den+=(v-m)*(v-m);if(den==0)throw std::domain_error("constant series");std::vector<double>r(maxlag);for(std::size_t k=1;k<=maxlag;++k){double num=0;for(std::size_t t=k;t<x.size();++t)num+=(x[t]-m)*(x[t-k]-m);r[k-1]=num/den;}return r;}
TestResult ljung_box(std::span<const double>x,std::size_t lags,std::size_t fitted,double alpha){if(lags<=fitted)throw std::invalid_argument("lags must exceed fitted parameters");const auto r=autocorrelations(x,lags);double n=static_cast<double>(x.size()),q=0;for(std::size_t k=1;k<=lags;++k)q+=r[k-1]*r[k-1]/(n-static_cast<double>(k));q*=n*(n+2);double p=gamma_q(0.5*static_cast<double>(lags-fitted),0.5*q);return{q,p,p<alpha};}
TestResult jarque_bera(std::span<const double>x,double alpha){auto m=moments(x);double n=static_cast<double>(x.size());double jb=n/6*(m.skewness*m.skewness+0.25*m.excess_kurtosis*m.excess_kurtosis);double p=std::exp(-jb/2);return{jb,p,p<alpha};}
double durbin_watson(std::span<const double>e){if(e.size()<2)throw std::invalid_argument("need at least two residuals");double num=0,den=0;for(double v:e)den+=v*v;for(std::size_t i=1;i<e.size();++i){double d=e[i]-e[i-1];num+=d*d;}if(den==0)throw std::domain_error("all residuals are zero");return num/den;}
} // namespace kvant::stats
