#pragma once
#include <Eigen/Core>
#include <span>
#include <vector>
namespace kvant::control {
struct KalmanState { Eigen::VectorXd mean; Eigen::MatrixXd covariance; };
[[nodiscard]] KalmanState kalman_update(const KalmanState&,const Eigen::Ref<const Eigen::MatrixXd>& observation_matrix,const Eigen::Ref<const Eigen::VectorXd>& observation,const Eigen::Ref<const Eigen::MatrixXd>& observation_covariance);
class MultiplicativeWeights {
public:
 MultiplicativeWeights(std::size_t models,double learning_rate,double floor=1e-8);
 void update(std::span<const double> losses);
 [[nodiscard]] std::span<const double> weights()const noexcept{return weights_;}
private:double learning_rate_,floor_;std::vector<double>weights_;
};
}
