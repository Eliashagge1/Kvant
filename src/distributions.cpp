#include "kvant/stats/distributions.hpp"
#include "kvant/stats/descriptive.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <numbers>
#include <stdexcept>

namespace kvant::stats {
namespace {
double betacf(double a,double b,double x){
    constexpr int maxit=300; constexpr double eps=3e-14, fpmin=1e-300;
    double qab=a+b,qap=a+1,qam=a-1,c=1,d=1-qab*x/qap; if(std::abs(d)<fpmin)d=fpmin; d=1/d; double h=d;
    for(int m=1;m<=maxit;++m){ int m2=2*m; double aa=m*(b-m)*x/((qam+m2)*(a+m2)); d=1+aa*d;if(std::abs(d)<fpmin)d=fpmin;c=1+aa/c;if(std::abs(c)<fpmin)c=fpmin;d=1/d;h*=d*c;
      aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2)); d=1+aa*d;if(std::abs(d)<fpmin)d=fpmin;c=1+aa/c;if(std::abs(c)<fpmin)c=fpmin;d=1/d;double del=d*c;h*=del;if(std::abs(del-1)<eps)break; }
    return h;
}
double ibeta(double a,double b,double x){
    if(x<=0)return 0;
    if(x>=1)return 1;
    double bt=std::exp(std::lgamma(a+b)-std::lgamma(a)-std::lgamma(b)+a*std::log(x)+b*std::log1p(-x));
    return x<(a+1)/(a+b+2)?bt*betacf(a,b,x)/a:1-bt*betacf(b,a,1-x)/b;
}
void probability(double p){if(!(p>=0&&p<=1))throw std::invalid_argument("probability outside [0,1]");}
}
double normal_pdf(double x,double mu,double sigma){if(!(sigma>0))throw std::invalid_argument("sigma must be positive");double z=(x-mu)/sigma;return std::exp(-0.5*z*z)/(sigma*std::sqrt(2*std::numbers::pi));}
double normal_cdf(double x,double mu,double sigma){if(!(sigma>0))throw std::invalid_argument("sigma must be positive");return 0.5*std::erfc(-(x-mu)/(sigma*std::sqrt(2.0)));}
double student_t_pdf(double x,double nu){if(!(nu>0))throw std::invalid_argument("degrees of freedom must be positive");return std::exp(std::lgamma((nu+1)/2)-std::lgamma(nu/2))/(std::sqrt(nu*std::numbers::pi)*std::pow(1+x*x/nu,(nu+1)/2));}
double student_t_cdf(double x,double nu){if(!(nu>0))throw std::invalid_argument("degrees of freedom must be positive");double q=ibeta(nu/2,0.5,nu/(nu+x*x));return x>=0?1-0.5*q:0.5*q;}
double student_t_quantile(double p,double nu){probability(p);if(p==0)return -std::numeric_limits<double>::infinity();if(p==1)return std::numeric_limits<double>::infinity();double lo=-1,hi=1;while(student_t_cdf(lo,nu)>p)lo*=2;while(student_t_cdf(hi,nu)<p)hi*=2;for(int i=0;i<160;++i){double mid=(lo+hi)/2;if(student_t_cdf(mid,nu)<p)lo=mid;else hi=mid;}return(lo+hi)/2;}
std::pair<double,double> mean_confidence_interval(std::span<const double>x,double confidence){if(x.size()<2)throw std::invalid_argument("need at least two observations");probability(confidence);if(confidence==0||confidence==1)throw std::invalid_argument("confidence must be in (0,1)");double m=mean(x),se=std::sqrt(sample_variance(x)/static_cast<double>(x.size()));double t=student_t_quantile(0.5+confidence/2,static_cast<double>(x.size()-1));return{m-t*se,m+t*se};}
double bayes_update(double prior,double lt,double lf){probability(prior);probability(lt);probability(lf);double a=prior*lt,b=(1-prior)*lf;if(a+b==0)throw std::domain_error("evidence has zero probability");return a/(a+b);}
double bonferroni_alpha(double a,std::size_t m){probability(a);if(m==0)throw std::invalid_argument("tests must be positive");return a/static_cast<double>(m);}
double bonferroni_adjusted_p(double p,std::size_t m){probability(p);if(m==0)throw std::invalid_argument("tests must be positive");return std::min(1.0,p*static_cast<double>(m));}
} // namespace kvant::stats
