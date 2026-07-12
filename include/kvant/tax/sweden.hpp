#pragma once
#include "kvant/money/fixed.hpp"
#include <map>
#include <optional>
#include <string>
#include <vector>
namespace kvant::tax {
enum class AccountType{isk,taxable};enum class LotMethod{average_cost,fifo,lifo,hifo,specific_id};
struct RuleVersion{int tax_year{};money::Fixed capital_tax_rate,isk_standard_rate,isk_allowance_sek;};
struct Lot{std::string id,asset_id;money::Fixed quantity,cost_sek;long long acquired_at{};};
struct Disposal{money::Fixed proceeds_sek,cost_sek,gain_sek;std::vector<std::string>consumed_lots;};
struct IskQuarter{money::Fixed opening_value_sek,deposits_sek;};
class SwedishTaxLedger{public:SwedishTaxLedger(AccountType,std::vector<RuleVersion>);void acquire(Lot);[[nodiscard]]Disposal dispose(const std::string&asset,money::Fixed quantity,money::Fixed proceeds,LotMethod,const std::vector<std::string>&specific={});void record_dividend(money::Fixed gross,money::Fixed withheld);void record_interest(money::Fixed income,money::Fixed expense);void record_fx_gain(money::Fixed realized,money::Fixed unrealized);[[nodiscard]]money::Fixed isk_capital_base(const std::vector<IskQuarter>&)const;[[nodiscard]]money::Fixed estimated_tax(int year)const;private:RuleVersion rule(int)const;AccountType type_;std::vector<RuleVersion>rules_;std::vector<Lot>lots_;money::Fixed realized_{0,100},dividends_{0,100},withholding_{0,100},interest_income_{0,100},interest_expense_{0,100},fx_realized_{0,100},fx_unrealized_{0,100};std::map<int,money::Fixed>isk_base_;};
}
