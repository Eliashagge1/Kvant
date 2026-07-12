#pragma once
#include "kvant/control/drift.hpp"
#include "kvant/control/journal.hpp"
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
namespace kvant::control {
enum class AdjustmentTier{none,online_update,ensemble_reweight,retrain};
struct Policy{std::size_t cooldown_days{20},shadow_minimum_observations{20};double shadow_required_improvement{0.02};};
struct Decision{bool drift{};AdjustmentTier tier{AdjustmentTier::none};bool retrain_requested{};};
class SelfCorrectionLoop{
public:
 SelfCorrectionLoop(Journal&,Policy,PageHinkley,Cusum,std::filesystem::path retrain_queue);
 void predict(const PredictionRecord&);
 [[nodiscard]]Decision resolve(const PredictionRecord&,double actual,std::int64_t resolved_at,std::size_t trading_day,AdjustmentTier preferred_tier);
 void compare_shadow(const ShadowComparison&);
 [[nodiscard]]bool candidate_can_control()const noexcept;
 void promote_candidate(const std::string& version,std::int64_t timestamp);
private:void request_retrain(const PredictionRecord&,double,std::int64_t);
 Journal&journal_;Policy policy_;PageHinkley page_hinkley_;Cusum cusum_;std::filesystem::path retrain_queue_;std::optional<std::size_t>last_adjustment_day_;std::size_t shadow_count_{};double incumbent_loss_{},candidate_loss_{};bool candidate_ready_{};
};
}
