#include "kvant/control/drift.hpp"
#include "kvant/control/online_updates.hpp"
#include "kvant/execution/paper_trader.hpp"
#include <cmath>
#include <iostream>
#include <vector>
struct J:kvant::execution::ExecutionJournal{int fills{};void log_fill(const kvant::execution::PaperFill&)override{++fills;}void log_equity(std::int64_t,double,double,double)override{}};
int main(){kvant::control::PageHinkley p(.01,.5,5);bool detected=false;for(int i=0;i<20;++i)detected|=p.update(i<8?0.0:1.0).detected;if(!detected)return 1;kvant::control::MultiplicativeWeights w(2,.5);double l[]={0.0,1.0};w.update(l);if(w.weights()[0]<=w.weights()[1])return 2;J j;kvant::execution::PaperTrader trader({100000,.001,1,.1},j);auto f=trader.execute({"1","ABC",1,100},{"ABC",2,99,101,100,10000});if(f.price<=101||j.fills!=1)return 3;std::cout<<"Phase 9-11 tests passed\n";}
