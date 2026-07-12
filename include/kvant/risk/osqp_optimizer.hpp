#pragma once
#include <Eigen/Core>
#include <vector>
namespace kvant::risk {struct Limits{Eigen::VectorXd lower,upper;Eigen::MatrixXd sector_exposure;Eigen::VectorXd sector_caps;double gross_leverage{1};};struct OsqpResult{Eigen::VectorXd weights;int status{};double objective{},primal_residual{},dual_residual{};};[[nodiscard]]OsqpResult solve_osqp(const Eigen::MatrixXd&covariance,const Eigen::VectorXd&alpha,const Eigen::VectorXd&current,const Eigen::VectorXd&turnover_cost,const Limits&limits,double risk_aversion);}
