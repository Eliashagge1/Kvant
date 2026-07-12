#include "kvant/stats/descriptive.hpp"
#include <cmath>
#include <stdexcept>

namespace kvant::stats {
namespace { void check(std::span<const double> x, std::size_t n) {
    if (x.size() < n) throw std::invalid_argument("insufficient observations");
    for (double v : x) if (!std::isfinite(v)) throw std::invalid_argument("non-finite observation");
}}

double mean(std::span<const double> x) {
    check(x, 1); double m=0.0; std::size_t n=0;
    for(double v:x) m += (v-m)/static_cast<double>(++n);
    return m;
}

double sample_variance(std::span<const double> x) {
    check(x, 2); double m=0.0,m2=0.0; std::size_t n=0;
    for(double v:x){ ++n; double d=v-m; m+=d/static_cast<double>(n); m2+=d*(v-m); }
    return m2/static_cast<double>(n-1);
}

double sample_covariance(std::span<const double> x, std::span<const double> y) {
    if(x.size()!=y.size()) throw std::invalid_argument("size mismatch");
    check(x,2); check(y,2);
    double mx=0,my=0,c=0; std::size_t n=0;
    for(std::size_t i=0;i<x.size();++i){ ++n; double dx=x[i]-mx; mx+=dx/static_cast<double>(n); double dy=y[i]-my; my+=dy/static_cast<double>(n); c+=dx*(y[i]-my); }
    return c/static_cast<double>(n-1);
}

Moments moments(std::span<const double> x) {
    check(x,4); const double m=mean(x); double m2=0,m3=0,m4=0;
    for(double v:x){double d=v-m,d2=d*d;m2+=d2;m3+=d2*d;m4+=d2*d2;}
    const double n=static_cast<double>(x.size()); const double s2=m2/(n-1.0);
    if(s2==0.0) return {x.size(),m,0,0,0,0};
    const double g1=(n/((n-1.0)*(n-2.0)))*(m3/std::pow(std::sqrt(s2),3));
    const double g2=(n*(n+1.0)/((n-1.0)*(n-2.0)*(n-3.0)))*(m4/(s2*s2))-(3.0*(n-1.0)*(n-1.0)/((n-2.0)*(n-3.0)));
    return {x.size(),m,s2,std::sqrt(s2),g1,g2};
}
} // namespace kvant::stats
