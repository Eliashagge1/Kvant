#include "kvant/control/online_updates.hpp"
#include <Eigen/Cholesky>
#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>
namespace kvant::control {
KalmanState kalman_update(const KalmanState&s,const Eigen::Ref<const Eigen::MatrixXd>&h,const Eigen::Ref<const Eigen::VectorXd>&z,const Eigen::Ref<const Eigen::MatrixXd>&r){const auto n=s.mean.size();if(n==0||s.covariance.rows()!=n||s.covariance.cols()!=n||h.cols()!=n||h.rows()!=z.size()||r.rows()!=z.size()||r.cols()!=z.size()||!s.mean.allFinite()||!s.covariance.allFinite()||!h.allFinite()||!z.allFinite()||!r.allFinite())throw std::invalid_argument("invalid Kalman dimensions or values");Eigen::MatrixXd innovation_covariance=h*s.covariance*h.transpose()+r;Eigen::LDLT<Eigen::MatrixXd>ldlt(innovation_covariance);if(ldlt.info()!=Eigen::Success||!ldlt.isPositive())throw std::domain_error("innovation covariance is not positive definite");Eigen::MatrixXd gain=ldlt.solve(h*s.covariance).transpose();Eigen::VectorXd mean=s.mean+gain*(z-h*s.mean);Eigen::MatrixXd identity=Eigen::MatrixXd::Identity(n,n);Eigen::MatrixXd a=identity-gain*h;Eigen::MatrixXd covariance=a*s.covariance*a.transpose()+gain*r*gain.transpose();covariance=(covariance+covariance.transpose())*.5;return{std::move(mean),std::move(covariance)};}
MultiplicativeWeights::MultiplicativeWeights(std::size_t n,double eta,double floor):learning_rate_(eta),floor_(floor),weights_(n,1.0/static_cast<double>(n)){if(!n||eta<=0||floor<0||floor*static_cast<double>(n)>=1)throw std::invalid_argument("invalid ensemble settings");}
void MultiplicativeWeights::update(std::span<const double>losses){if(losses.size()!=weights_.size())throw std::invalid_argument("loss size mismatch");for(std::size_t i=0;i<losses.size();++i){if(!std::isfinite(losses[i])||losses[i]<0)throw std::invalid_argument("loss must be finite and nonnegative");weights_[i]=std::max(floor_,weights_[i]*std::exp(-learning_rate_*losses[i]));}double sum=std::accumulate(weights_.begin(),weights_.end(),0.0);for(double&w:weights_)w/=sum;}
}
