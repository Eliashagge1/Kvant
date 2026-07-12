#include "kvant/models/tree_model.hpp"
#include "kvant/security/artifact.hpp"
#include <stdexcept>
#ifdef KVANT_WITH_TL2CGEN_RUNTIME
#include <tl2cgen/predictor.h>
#endif
namespace kvant::models {
struct TreeModel::Impl{
 std::size_t features{};
#ifdef KVANT_WITH_TL2CGEN_RUNTIME
 std::unique_ptr<tl2cgen::predictor::Predictor> predictor;
#endif
};
TreeModel::TreeModel(const std::filesystem::path&lib,const std::filesystem::path&sig,const std::filesystem::path&key,const std::filesystem::path&root,std::size_t n):p_(std::make_unique<Impl>()){security::enforce_safe_artifact_path(lib,root);if(!security::verify_ed25519(lib,sig,key))throw std::runtime_error("invalid model signature");p_->features=n;
#ifdef KVANT_WITH_TL2CGEN_RUNTIME
 p_->predictor=std::make_unique<tl2cgen::predictor::Predictor>(lib.string(),1);
 if(static_cast<std::size_t>(p_->predictor->GetNumFeature())!=n)throw std::runtime_error("tree feature mismatch");
#else
 (void)lib;throw std::runtime_error("TL2cgen runtime disabled at build time");
#endif
}
TreeModel::~TreeModel()=default;
std::vector<double>TreeModel::predict(std::span<const double>x)const{if(x.size()!=p_->features)throw std::invalid_argument("feature count mismatch");
#ifdef KVANT_WITH_TL2CGEN_RUNTIME
 auto matrix=tl2cgen::predictor::DMatrix::CreateDense(x.data(),1,x.size(),std::numeric_limits<double>::quiet_NaN());return p_->predictor->Predict(matrix.get(),false);
#else
 return{};
#endif
}}
