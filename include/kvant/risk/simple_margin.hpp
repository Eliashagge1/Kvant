#pragma once
#include "kvant/money/fixed.hpp"
#include <map>
#include <span>
#include <string>
#include <vector>
namespace kvant::risk {struct Holding{std::string asset_id;money::Fixed quantity,price;};struct MarginConfig{long double initial_rate{},maintenance_rate{};};struct MarginDecision{bool block_new_risk{},maintenance_breach{};money::Fixed initial_required{0,100},maintenance_required{0,100},equity{0,100};std::vector<std::pair<std::string,money::Fixed>>suggested_liquidations;};[[nodiscard]]MarginDecision evaluate_simple_margin(std::span<const Holding>,money::Fixed cash,const MarginConfig&,bool generate_suggestions);}
