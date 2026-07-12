#include "kvant/execution/paper_trader.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace kvant::execution {
PaperTrader::PaperTrader(PaperConfig c,ExecutionJournal&j):config_(c),journal_(j),cash_(c.initial_cash){if(c.initial_cash<=0||c.commission_per_unit<0||c.minimum_commission<0||c.impact_coefficient<0)throw std::invalid_argument("invalid paper configuration");}
PaperFill PaperTrader::execute(const PaperOrder&o,const Quote&q){if(o.symbol!=q.symbol||o.order_id.empty()||!std::isfinite(o.quantity)||o.quantity==0||q.ask<q.bid||q.bid<=0||q.adv<=0||q.timestamp<o.submitted_at)throw std::invalid_argument("invalid paper order or quote");double midpoint=(q.bid+q.ask)/2,spread=q.ask-q.bid,sign=o.quantity>0?1:-1,impact=midpoint*config_.impact_coefficient*std::sqrt(std::abs(o.quantity)/q.adv),price=midpoint+sign*(spread/2+impact),commission=std::max(config_.minimum_commission,std::abs(o.quantity)*config_.commission_per_unit);cash_-=o.quantity*price+commission;positions_[o.symbol]+=o.quantity;PaperFill fill{o.order_id,o.symbol,q.timestamp,o.quantity,price,commission,impact};journal_.log_fill(fill);return fill;}
double PaperTrader::mark_to_market(const std::vector<Quote>&quotes)const{double equity=cash_;for(const auto&q:quotes){auto it=positions_.find(q.symbol);if(it!=positions_.end()){if(q.close<=0||!std::isfinite(q.close))throw std::invalid_argument("invalid mark");equity+=it->second*q.close;}}return equity;}
void PaperTrader::record_divergence(std::int64_t t,double expected,double live,double noise){if(noise<=0||!std::isfinite(expected)||!std::isfinite(live))throw std::invalid_argument("invalid divergence inputs");double divergence=live-expected,z=divergence/noise;journal_.log_equity(t,live,expected,z);}
}
