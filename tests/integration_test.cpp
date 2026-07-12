#include "kvant/backtest/multi_asset.hpp"
#include <cmath>
#include <iostream>
int main(){using namespace kvant::backtest;std::vector<Bar>b{{1,"A",100,101,10000,1,1,0,false},{1,"B",50,49,10000,.5,1,0,false},{2,"A",102,103,10000,1,1,0,false},{2,"B",48,50,10000,.5,1,0,false},{3,"A",104,104,10000,1,1,0,false},{3,"B",51,51,10000,.5,1,0,true}};Targets t{{1,{{"A",.5},{"B",.5}}},{2,{{"A",.6},{"B",.4}}}};auto r=run_multi_asset(b,t,{100000,.001,1,.05,.1});if(r.days.size()!=3||r.fills.empty()||!std::isfinite(r.days.back().equity))return 1;if(std::abs(r.positions["B"])>1e-12)return 2;std::cout<<"integration passed\n";}
