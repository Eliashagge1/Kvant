#include "kvant/monitoring/metrics.hpp"
#include "kvant/monitoring/safeguards.hpp"
#include <cmath>
#include <iostream>
#include <vector>
int main(){using namespace kvant::monitoring;std::vector<double>p{1,2,3,4},y{1.1,1.9,3.2,3.8};if(pearson_information_coefficient(p,y)<.9)return 1;std::vector<double>prob{.8,.2},binary{1,0};if(std::abs(brier_score(prob,binary)-.04)>1e-12)return 2;auto d=automatic_deflated_sharpe(1,.04,10,0,0,252);if(!d.required||d.probability<0||d.probability>1)return 3;auto none=automatic_deflated_sharpe(1,.04,1,0,0,252);if(none.required)return 4;std::vector<double>h{1,2,4},ic{.2,.1,.05};if(alpha_decay_half_life(h,ic)<=0)return 5;std::cout<<"Phase 12-13 tests passed\n";}
