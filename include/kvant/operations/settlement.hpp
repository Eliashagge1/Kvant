#pragma once
#include "kvant/money/fixed.hpp"
#include <map>
#include <set>
#include <optional>
#include <string>
#include <vector>
namespace kvant::operations {struct Calendar{std::set<long long>holidays;[[nodiscard]]long long add_business_days(long long date,int days)const;};struct Convention{std::string market,currency;int business_days{1};};struct Settlement{std::string id,asset_id,currency;long long trade_date{},due_date{};money::Fixed amount{0,100};bool settled{},failed{};};struct ReviewItem{std::string id,type,raw_payload,reason;long long deadline{};};class SettlementBook{public:void configure(Convention,Calendar);Settlement create(std::string id,std::string asset,std::string market,std::string currency,long long trade_date,money::Fixed amount);void settle(const std::string&id);void mark_failures(long long now);[[nodiscard]]const std::vector<Settlement>&items()const{return items_;}private:std::map<std::pair<std::string,std::string>,std::pair<Convention,Calendar>>config_;std::vector<Settlement>items_;};class ReviewQueue{public:void quarantine(ReviewItem);[[nodiscard]]const std::vector<ReviewItem>&items()const{return items_;}private:std::vector<ReviewItem>items_;};}
