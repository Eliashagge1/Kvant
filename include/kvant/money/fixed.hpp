#pragma once
#include <cstdint>
#include <stdexcept>
namespace kvant::money {
enum class Rounding{half_even,half_away,down,up};
class Fixed {
public:
 constexpr Fixed()=default;constexpr Fixed(std::int64_t raw,std::int64_t scale):raw_(raw),scale_(scale){if(scale<=0)throw std::invalid_argument("scale");}
 static Fixed from_decimal(long double value,std::int64_t scale,Rounding mode=Rounding::half_even);
 [[nodiscard]]constexpr std::int64_t raw()const{return raw_;}[[nodiscard]]constexpr std::int64_t scale()const{return scale_;}
 [[nodiscard]]long double decimal()const{return static_cast<long double>(raw_)/scale_;}
 [[nodiscard]]Fixed rescale(std::int64_t,Rounding mode=Rounding::half_even)const;
 friend Fixed operator+(Fixed,Fixed);friend Fixed operator-(Fixed,Fixed);friend Fixed multiply(Fixed,Fixed,std::int64_t,Rounding);
private:std::int64_t raw_{},scale_{1};
};
inline constexpr std::int64_t quantity_scale=1'000'000,price_scale=1'000'000,fx_scale=100'000'000,rate_scale=100'000'000;
}
