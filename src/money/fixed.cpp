#include "kvant/money/fixed.hpp"
#include <cmath>
#include <limits>
namespace kvant::money {namespace {
__extension__ typedef __int128 int128;
std::int64_t checked(int128 v){if(v>std::numeric_limits<std::int64_t>::max()||v<std::numeric_limits<std::int64_t>::min())throw std::overflow_error("fixed-point overflow");return static_cast<std::int64_t>(v);}
std::int64_t divide(int128 numerator,int128 denominator,Rounding mode){if(denominator<=0)throw std::invalid_argument("denominator");bool negative=numerator<0;int128 a=negative?-numerator:numerator,q=a/denominator,r=a%denominator;bool increment=false;if(mode==Rounding::half_away)increment=2*r>=denominator;else if(mode==Rounding::half_even)increment=2*r>denominator||(2*r==denominator&&(q&1));else if(mode==Rounding::up)increment=r!=0&&!negative;else if(mode==Rounding::down)increment=r!=0&&negative;if(increment)++q;return checked(negative?-q:q);}
}
Fixed Fixed::from_decimal(long double value,std::int64_t scale,Rounding mode){if(!std::isfinite(value)||scale<=0)throw std::invalid_argument("decimal");long double scaled=value*scale;long double floorv=std::floor(std::abs(scaled)),fraction=std::abs(scaled)-floorv;int128 q=static_cast<int128>(floorv);bool inc=mode==Rounding::half_away?fraction>=.5L:mode==Rounding::half_even?(fraction>.5L||(fraction==.5L&&(q&1))):mode==Rounding::up?(scaled>0&&fraction>0):(scaled<0&&fraction>0);if(inc)++q;if(scaled<0)q=-q;return{checked(q),scale};}
Fixed Fixed::rescale(std::int64_t scale,Rounding mode)const{return{divide(static_cast<int128>(raw_)*scale,scale_,mode),scale};}
Fixed operator+(Fixed a,Fixed b){if(a.scale_!=b.scale_)throw std::invalid_argument("scale mismatch");return{checked(static_cast<int128>(a.raw_)+b.raw_),a.scale_};}
Fixed operator-(Fixed a,Fixed b){if(a.scale_!=b.scale_)throw std::invalid_argument("scale mismatch");return{checked(static_cast<int128>(a.raw_)-b.raw_),a.scale_};}
Fixed multiply(Fixed a,Fixed b,std::int64_t scale,Rounding mode){return{divide(static_cast<int128>(a.raw_)*b.raw_*scale,static_cast<int128>(a.scale_)*b.scale_,mode),scale};}
}
