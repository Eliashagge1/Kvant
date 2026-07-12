#pragma once
#include <cstdint>
#include <map>
#include <string>
namespace kvant::monitoring {
struct ExperimentRecord{std::string run_id,experiment_name,git_commit,code_version,data_snapshot,feature_spec_hash,model_artifact_hash;std::int64_t started_at{},completed_at{};std::map<std::string,std::string>parameters;std::map<std::string,double>metrics;std::size_t tested_variants{};};
class ExperimentJournal{public:virtual~ExperimentJournal()=default;virtual void append(const ExperimentRecord&)=0;};
void validate_experiment(const ExperimentRecord&);
}
