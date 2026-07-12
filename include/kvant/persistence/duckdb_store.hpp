#pragma once
#include <filesystem>
#include <memory>
#include <string>
#include <vector>
namespace kvant::persistence {struct Prediction{std::string id,model,symbol,features_json;long long made_at{},resolve_after{};double value{},lower{},upper{};bool shadow{};};class DuckDbStore{public:explicit DuckDbStore(const std::filesystem::path&);~DuckDbStore();DuckDbStore(DuckDbStore&&)noexcept;void migrate();void append_prediction(const Prediction&);void resolve_prediction(const std::string&id,long long resolved_at,double actual,double error);void append_experiment(const std::string&run_id,const std::string&git_commit,const std::string&parameters_json,const std::string&metrics_json,unsigned variants);[[nodiscard]]std::vector<Prediction> unresolved(long long as_of)const;private:struct Impl;std::unique_ptr<Impl>p_;};}
