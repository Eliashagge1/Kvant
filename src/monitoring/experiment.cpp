#include "kvant/monitoring/experiment.hpp"
#include <cmath>
#include <stdexcept>
namespace kvant::monitoring {void validate_experiment(const ExperimentRecord&r){if(r.run_id.empty()||r.experiment_name.empty()||r.git_commit.empty()||r.data_snapshot.empty()||r.feature_spec_hash.empty()||r.started_at<=0||r.completed_at<r.started_at||r.tested_variants==0)throw std::invalid_argument("incomplete experiment record");for(const auto&[k,v]:r.metrics)if(k.empty()||!std::isfinite(v))throw std::invalid_argument("invalid experiment metric");}}
