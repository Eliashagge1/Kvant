#include "kvant/money/fixed.hpp"
#include "kvant/operations/settlement.hpp"
#include "kvant/risk/simple_margin.hpp"
#include "kvant/tax/sweden.hpp"
#include <cmath>
#include <iostream>
using kvant::money::Fixed;
int main(){auto q=Fixed::from_decimal(1.2345675L,1'000'000);if(q.raw()!=1234568)return 1;kvant::tax::SwedishTaxLedger tax(kvant::tax::AccountType::taxable,{{2026,Fixed::from_decimal(.30,100000000),Fixed::from_decimal(.0355,100000000),Fixed::from_decimal(300000,100)}});tax.acquire({"l1","A",Fixed::from_decimal(10,1'000'000),Fixed::from_decimal(1000,100),1});tax.acquire({"l2","A",Fixed::from_decimal(10,1'000'000),Fixed::from_decimal(2000,100),2});auto d=tax.dispose("A",Fixed::from_decimal(10,1'000'000),Fixed::from_decimal(2500,100),kvant::tax::LotMethod::average_cost);if(std::abs(d.gain_sek.decimal()-1000)>1e-9)return 2;kvant::operations::SettlementBook b;b.configure({"US","SEK",1},{});auto s=b.create("s1","A","US","SEK",1,Fixed::from_decimal(-1000,100));if(s.due_date<=1)return 3;b.mark_failures(s.due_date+1);if(!b.items()[0].failed)return 4;std::vector<kvant::risk::Holding>h{{"A",Fixed::from_decimal(100,1'000'000),Fixed::from_decimal(100,1'000'000)}};auto m=kvant::risk::evaluate_simple_margin(h,Fixed::from_decimal(-8000,100),{.5,.3},true);if(!m.block_new_risk||!m.maintenance_breach||m.suggested_liquidations.empty())return 5;std::cout<<"synthetic Swedish fixtures passed\n";}
