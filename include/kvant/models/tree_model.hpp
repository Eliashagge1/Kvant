#pragma once
#include <filesystem>
#include <memory>
#include <span>
#include <vector>
namespace kvant::models {class TreeModel{public:TreeModel(const std::filesystem::path&library,const std::filesystem::path&signature,const std::filesystem::path&public_key,const std::filesystem::path&allowlisted_root,std::size_t features);~TreeModel();[[nodiscard]]std::vector<double>predict(std::span<const double>)const;private:struct Impl;std::unique_ptr<Impl>p_;};}
