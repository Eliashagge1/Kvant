#pragma once
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>
namespace kvant::execution {
struct Quote{std::string symbol;std::int64_t timestamp{};double bid{},ask{},close{},adv{};};
struct PaperOrder{std::string order_id,symbol;std::int64_t submitted_at{};double quantity{};};
struct PaperFill{std::string order_id,symbol;std::int64_t timestamp{};double quantity{},price{},commission{},impact{};};
struct PaperConfig{double initial_cash{1000000},commission_per_unit{},minimum_commission{},impact_coefficient{};};
class ExecutionJournal{public:virtual~ExecutionJournal()=default;virtual void log_fill(const PaperFill&)=0;virtual void log_equity(std::int64_t,double,double,double)=0;};
class PaperTrader{public:PaperTrader(PaperConfig,ExecutionJournal&);[[nodiscard]]PaperFill execute(const PaperOrder&,const Quote&);[[nodiscard]]double mark_to_market(const std::vector<Quote>&)const;void record_divergence(std::int64_t,double expected_backtest_return,double live_return,double expected_noise_std);private:PaperConfig config_;ExecutionJournal&journal_;double cash_;std::unordered_map<std::string,double>positions_;};
}
