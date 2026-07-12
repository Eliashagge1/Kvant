#pragma once
#include <map>
#include <string>
#include <vector>
namespace kvant::backtest {struct Bar{long long time{};std::string symbol;double open{},close{},adv{},spread{},split_factor{1},cash_dividend{};bool delisted{};};struct Order{std::string symbol;double target_weight{};};struct Fill{long long time{};std::string symbol;double quantity{},price{},commission{},impact{};};struct DayResult{long long time{};double equity{},daily_return{},cash{},gross_exposure{},turnover{};};struct Config{double initial_cash{1e6},commission_per_unit{},minimum_commission{},impact_coefficient{},max_participation{.1};};struct Result{std::vector<DayResult>days;std::vector<Fill>fills;std::map<std::string,double>positions;};using Targets=std::map<long long,std::vector<Order>>;[[nodiscard]]Result run_multi_asset(std::vector<Bar>bars,const Targets&,const Config&);}
