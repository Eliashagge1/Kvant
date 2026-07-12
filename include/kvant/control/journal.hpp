#pragma once
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <vector>
namespace kvant::control {
struct PredictionRecord{std::string prediction_id,model_version,symbol;std::int64_t made_at{},resolve_after{};double prediction{},lower{},upper{};std::vector<double>features;bool shadow{};};
struct ResolutionRecord{std::string prediction_id;std::int64_t resolved_at{};double actual{},error{};};
struct ShadowComparison{std::string incumbent_version,candidate_version;std::int64_t timestamp{};double incumbent_loss{},candidate_loss{};};
class Journal{public:virtual~Journal()=default;virtual void log_prediction(const PredictionRecord&)=0;virtual void log_resolution(const ResolutionRecord&)=0;virtual void log_shadow(const ShadowComparison&)=0;virtual void log_event(std::int64_t,const std::string&,const std::string&)=0;};
}
