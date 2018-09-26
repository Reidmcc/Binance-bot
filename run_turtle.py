##### Executer for the turtle_trade strategy, see turtle_trade.py for more
##### I should really object-ify the coin cycles
from turtle_trade import turtle


pair = "XLMBTC"
interval = "12h"
limit = 1000
pip_sats = 1
# capital in sats
# capital = 4000000
capital = 1
# price_mult = 1E8
price_mult = 1
enter_trig = 20
exit_trig = 10
total_lost_longs = 0
total_won_longs = 0
total_lost_shorts = 0
total_won_shorts = 0

XLM_turtle = turtle()
XLM_turtle.set_params(pair, interval, pip_sats, capital, limit, exit_trig, enter_trig, price_mult)
XLM_results = XLM_turtle.find_trades()
post_XLM_capital = XLM_results[0]
total_lost_longs += XLM_results [1]
total_won_longs += XLM_results [2]
total_lost_shorts += XLM_results [3]
total_won_shorts += XLM_results [4]
best_XLM_gain = XLM_results[5]
worst_XLM_loss = XLM_results[6]



pair = "LTCBTC"
pip_sats = 1
LTC_turtle = turtle()
LTC_turtle.set_params(pair, interval, pip_sats, post_XLM_capital, limit, exit_trig, enter_trig, price_mult)
LTC_results = LTC_turtle.find_trades()
post_LTC_capital = LTC_results[0]
total_lost_longs += LTC_results [1]
total_won_longs += LTC_results [2]
total_lost_shorts += LTC_results [3]
total_won_shorts += LTC_results [4]
best_LTC_gain = LTC_results[5]
worst_LTC_loss = LTC_results[6]



pair = "XMRBTC"
pip_sats = 1
XMR_turtle = turtle()
XMR_turtle.set_params(pair, interval, pip_sats, post_LTC_capital, limit, exit_trig, enter_trig, price_mult)
XMR_results = XMR_turtle.find_trades()
post_XMR_capital = XMR_results[0]
total_lost_longs += XMR_results [1]
total_won_longs += XMR_results [2]
total_lost_shorts += XMR_results [3]
total_won_shorts += XMR_results [4]
best_XMR_gain = XMR_results[5]
worst_XMR_loss = XMR_results[6]



pair = "BNBBTC"
pip_sats = 1
BNB_turtle = turtle()
BNB_turtle.set_params(pair, interval, pip_sats, post_XMR_capital, limit, exit_trig, enter_trig, price_mult)
BNB_results = BNB_turtle.find_trades()
post_BNB_capital = BNB_results[0]
total_lost_longs += BNB_results [1]
total_won_longs += BNB_results [2]
total_lost_shorts += BNB_results [3]
total_won_shorts += BNB_results [4]
best_BNB_gain = BNB_results[5]
worst_BNB_loss = BNB_results[6]



pair = "TUSDBTC"
pip_sats = 1
TUSD_turtle = turtle()
TUSD_turtle.set_params(pair, interval, pip_sats, post_XMR_capital, limit, exit_trig, enter_trig, price_mult)
TUSD_results = TUSD_turtle.find_trades()
final_cap = TUSD_results[0]
total_lost_longs += TUSD_results [1]
total_won_longs += TUSD_results [2]
total_lost_shorts += TUSD_results [3]
total_won_shorts += TUSD_results [4]
best_TUSD_gain = TUSD_results[5]
worst_TUSD_loss = TUSD_results[6]

print("Profit/loss on XLM was: " + "{:.8f}".format(post_XLM_capital - capital))
print("Profit/loss on LTC was: " + "{:.8f}".format(post_LTC_capital - post_XLM_capital))
print("Profit/loss on XMR was: " + "{:.8f}".format(post_XMR_capital - post_LTC_capital))
print("Profit/loss on BNB was: " + "{:.8f}".format(post_BNB_capital - post_XMR_capital))
# print("Profit/loss on ADA was: " + "{:.8f}".format(post_ADA_capital - post_BNB_capital))
print("Profit/loss on TUSD was: " + "{:.8f}".format(final_cap - post_BNB_capital))
print("Final capital = " + "{:.8f}".format(final_cap))
print("Gain/loss percentage = " + str(final_cap / capital))

print("Long trades: won " + str(total_won_longs) + " lost " + str(total_lost_longs))
# print("Win ratio = " + str(total_won_longs / (total_won_longs + total_lost_longs)))
# print("Short trades: won " + str(total_won_shorts) + " lost " + str(total_lost_shorts))

print("Best XLM gain = " + best_XLM_gain)
# print("Worst XLM loss = " + worst_XLM_loss)
print("Best LTC gain = " + best_LTC_gain)
# print("Worst LTC loss = " + worst_LTC_loss)
print("Best XMR gain = " + best_XMR_gain)
# print("Worst XMR loss = " + worst_XMR_loss)
print("Best BNB gain = " + best_BNB_gain)
# print("Worst BNB loss = " + worst_BNB_loss)
print("Best TUSD gain = " + best_TUSD_gain)
# print("Worst TUSD loss = " + worst_TUSD_loss)
