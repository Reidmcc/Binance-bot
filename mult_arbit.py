##### Code for cross-pair arbitrage with multiple pair-sets simultaneously
##### Theoretically can run any number of pair-sets but agility goes down with each set added. Probably keep it to 4 or less.


from api import BinanceAPI
client = BinanceAPI('[API key]','[API secret]')
import time
# import datetime
from excepts import MalformedRequest, StatusUnknown, InternalError
from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from http.client import HTTPException
from urllib3.exceptions import ProtocolError
from log import log_c


class Trades:
    def __init__(self):

        self.vars_set = False

        self.t_1_price = -1
        self.t_2_price = -1
        self.t_3_price = -1

        self.t_2_orig_price = -1
        self.t_3_orig_price = -1

        self.update_interval = 10
        self.bite_interval = 30
        self.cycle_fail = False
        self.no_bites = False

        # self.t_2_stop_trigger = 0.98
        self.t_2_loss_rate_trig = .025
        self.t_2_stop_price = 0.95
        self.t_2_backstop_price = 1.05
        self.t_2_stoploss = False

        self.t_2_backtraded = False

        self.t_2_reverse_trigger = 0.99
        self.t_2_reverse_price = 0.991
        self.t_2_reversal = False

        self.t_3_stop_trigger = 1.02
        self.t_3_stop_price = 1.05
        self.t_3_stoploss = False

        self.base_rate = 1.0045
        self.t_1_ratio = .95

        self.t_1_price_form = '0'
        self.t_2_price_form = '0'
        self.t_3_price_form = '0'

        self.t_2_min_amt = 100
        self.t_2_min_val = 100

        self.t_1_min_amt = 1
        self.t_1_min_val = 100

        self.t_3_min_val = 0.001

        self.t_1_pip_pad = 1

        self.alt_bal = -1
        self.static_t1_value = 0

        self.target_BNB_bal = 1.70
        self.BNB_trade_amt = -1

        self.target_BTC_bal = 0.00133

        self.last_BNB_t1_price = -1
        self.last_ETH_t1_price = -1
        self.last_t3_price = -1

        self.t_1_orig_quant = -1
        self.t_2_orig_quant = -1
        self.t_3_orig_quant = -1

        self.t_1_decimal = False
        self.t_2_decimal = False
        self.t_3_decimal = 0

        self.t_1_status = 'not_placed'
        self.t_2_status = 'not_placed'
        self.t_3_status = 'not_placed'

        self.t_1_orderID = '0'
        self.t_2_orderID = '0'
        self.t_3_orderID = '0'

        self.t_1_quant = 0
        self.t_2_quant = 0
        self.t_3_quant = 0

        self.t_1_executed = -1
        self.t_2_executed = -1
        self.t_3_executed = -1

        self.pair_1 = 'none'
        self.pair_2 = 'none'
        self.pair_3 = 'none'

        self.pair_1_pip = -1
        self.pair_2_pip = -1
        self.pair_3_pip = -1

        self.coin_1 = 'undefined'
        self.coin_2 = 'undefined'
        self.coin_3 = 'BTC'

        # self.valid_partial = False
        self.cancelled_partial = False

        self.t_2_fail_count = 0
        self.t_3_fail_count = 0

        self.cycle_count = 0

        self.checkpoint_t_1_placed = False
        self.checkpoint_t_1_bite_checked = False
        self.checkpoint_t_1_complete = False
        self.checkpoint_t_2_placed = False
        self.checkpoint_t_2_complete = False
        self.checkpoint_t_3_placed = False
        self.checkpoint_t_3_complete = False

        self.cyc_status = 'Initiated'

        self.partial_wait_count = 0

        self.lg = log_c()
        self.logfile = 'Default_log.txt'


    def set_params(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip, pair_3_pip,
                    alt_bal, t_1_imp_price, t_2_imp_price, t_3_imp_price):
        self.alt_bal = alt_bal

        self.t_1_price = t_1_imp_price
        self.t_2_price = t_2_imp_price
        self.t_3_price = t_3_imp_price

        self.lg.log('Original t_1 price = ' + str(self.t_1_price))
        self.lg.log('Original t_2 price = ' + str(self.t_2_price))
        self.lg.log('Original t_3 price = ' + str(self.t_3_price))

        self.pair_1 = pair_1
        self.pair_2 = pair_2
        self.pair_3 = pair_3

        self.pair_1_pip = float(pair_1_pip)
        self.pair_2_pip = float(pair_2_pip)
        self.pair_3_pip = float(pair_3_pip)

        self.t_1_price_form = str('{:.' + str(pair_1_pip)[-1:] + 'f}')
        self.t_2_price_form = str('{:.' + str(pair_2_pip)[-1:] + 'f}')
        self.t_3_price_form = str('{:.' + str(pair_3_pip)[-1:] + 'f}')

        if pair_1 == 'XLMBNB':
            self.t_1_min_val = 1
            self.t_1_decimal = 1
            self.t_2_min_val = 0.001
            self.t_2_min_amt = 1
            self.t_1_pip_pad = 1
            self.t_2_decimal = 2
            self.coin_1 = 'XLM'
            self.coin_2 = 'BNB'
            self.lg.log('Coin 2 is BNB')
        elif pair_1 == 'XLMETH':
            self.t_1_min_val = 0.01
            self.t_1_decimal = 0
            self.t_2_min_val = 0.001
            self.t_2_min_amt = 0.001
            self.t_1_pip_pad = 5
            self.t_2_decimal = 3
            self.coin_1 = 'XLM'
            self.coin_2 = 'ETH'
            self.lg.log('Coin 2 is ETH')
        elif pair_1 == 'ADABNB':
            self.t_1_min_val = 1
            self.t_1_decimal = 1
            self.t_2_min_val = 0.001
            self.t_2_min_amt = 1
            self.t_1_pip_pad = 1
            self.t_2_decimal = 2
            self.coin_1 = 'ADA'
            self.coin_2 = 'BNB'
            self.lg.log('Coin 2 is BNB')
        elif pair_1 == 'ADAETH':
            self.t_1_min_val = .01
            self.t_1_decimal = 0
            self.t_2_min_val = 0.001
            self.t_2_min_amt = 0.001
            self.t_1_pip_pad = 10
            self.t_2_decimal = 3
            self.coin_1 = 'ADA'
            self.coin_2 = 'ETH'
            self.lg.log('Coin 2 is ETH')
        else:
            self.cycle_fail = True
            self.lg.log("Coin 2 not recognized, input was: " + self.pair_1[:3])

    def run_cycle(self):

        # if not self.vars_set:

        if not self.cycle_fail and self.cyc_status != 'complete':
            if not self.checkpoint_t_1_placed:
                self.place_t_1()

            if self.checkpoint_t_1_placed and not self.checkpoint_t_1_bite_checked:
                self.cyc_status = 't_1 placed'
                self.bite_watch()

            if self.checkpoint_t_1_bite_checked and not self.checkpoint_t_1_complete:
                self.cyc_status = 't_1 bite-checked'
                self.t_1_part_watch()

            if self.checkpoint_t_1_complete and not self.checkpoint_t_2_placed:
                self.cyc_status = 't_1 complete'
                self.place_t_2()

            if self.checkpoint_t_2_placed and not self.checkpoint_t_2_complete:
                self.cyc_status = 't_2_placed'
                self.t_2_watch()

            if self.checkpoint_t_2_complete and not self.checkpoint_t_3_placed:
                if self.t_2_backtraded:
                    self.cyc_status = 'complete'
                else:
                    self.cyc_status = 't_2_complete'
                    self.place_t_3()

            if self.checkpoint_t_3_placed and not self.checkpoint_t_3_complete and not self.t_2_backtraded:
                self.cyc_status = 't_3 placed'
                self.t_3_watch()

        if self.checkpoint_t_3_complete:
            self.cyc_status = 'complete'
        elif self.cycle_fail == True:
            self.cyc_status = 'failed'

        # return self.cyc_status

    def cur_stat(self):
        cur_stat = self.cyc_status
        return cur_stat

    def place_t_1(self):
        self.t_1_quant = self.alt_bal * self.t_1_ratio

        self.lg.log('Before placing t_1, self.t_1_price = ' + str(self.t_1_price))
        self.lg.log('self.pair_1_pip = ' + str(self.pair_1_pip))
        self.lg.log('self.t_1_pip_pad was')

        if self.t_1_quant * self.t_1_price < self.t_1_min_val \
                or self.t_1_quant * self.t_1_price * self.t_2_price < self.t_2_min_val \
                or self.t_1_quant * self.t_1_price < self.t_2_min_amt:
            self.lg.log("Insufficient alt_bal to cycle")
            self.cycle_fail = True

        t_1_price_adj = self.t_1_price - (self.pair_1_pip * self.t_1_pip_pad)
        self.lg.log('Adjusted price came to: ' + str(t_1_price_adj))

        t_1 = self.place_order_retry(self.pair_1, self.quant_str_trim(self.t_1_quant, self.t_1_decimal),
                                     self.t_1_price_form.format(t_1_price_adj), 'sell')
        stat_check = t_1["status"]
        if stat_check != 'not_placed':
            self.t_1_orderID = t_1["orderID"]
            self.t_1_status = t_1["status"]
            self.t_1_price = float(self.t_1_price_form.format(t_1_price_adj))
            self.t_1_orig_quant = self.t_1_quant

            self.lg.log('Initial t_1 order ID = ' + str(self.t_1_orderID))
            self.lg.log('First retreived t_1 status = ' + self.t_1_status)

            self.checkpoint_t_1_placed = True
        else:
            self.lg.log('Initial t_1 order failed, cancelling cycle')
            self.cycle_fail = True


    def bite_watch(self):
        if self.t_1_status == 'NEW':
            self.cycle_count += 1
            self.t_1_status = self.get_order_stat_remaining(self.pair_1, self.t_1_orderID)["status"]
            if self.cycle_count >= self.bite_interval:
                self.ord_cancel(self.pair_1, self.t_1_orderID)
                time.sleep(.5)
                self.t_1_status = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)["status"]
                self.lg.log('No bites, cancelling out. Post-cancel status was: ' + self.t_1_status)
                self.no_bites = True
        else:
            self.checkpoint_t_1_bite_checked = True
            self.cycle_count = 0


    def t_1_part_watch(self):
        self.partial_wait_count += 1

        if (self.t_1_status == "PARTIALLY_FILLED" or self.t_1_status == 'NEW'):
            self.cycle_count += 1
            t_1_stat_get = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)
            self.t_1_status = t_1_stat_get["status"]
            t_1_remaining = t_1_stat_get["remaining"]

            if self.t_1_status != 'FILLED' and self.cycle_count >= self.update_interval:
                self.cycle_count = 0
                if (self.t_1_orig_quant - t_1_remaining) * self.t_1_price * self.t_2_price > self.t_2_min_val \
                        and (self.t_1_orig_quant - t_1_remaining) * self.t_1_price > self.t_2_min_amt:
                    self.ord_cancel(self.pair_1, self.t_1_orderID)
                    t_1_stat_get = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)
                    self.t_1_status = t_1_stat_get["status"]
                    self.lg.log('Partial sold amount is enough to cycle, moving on')
                    self.checkpoint_t_1_complete = True

                elif self.partial_wait_count >= 1000:
                    self.lg.log("This partial ain't moving, cancelling out")
                    self.ord_cancel(self.pair_1, self.t_1_orderID)
                    t_1_stat_get = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)
                    self.t_1_status = t_1_stat_get["status"]
                    self.checkpoint_t_1_complete = True
                    self.cancelled_partial = True
                else:
                    book_get = self.get_ord_book(self.pair_1)
                    book_fail = book_get["fail_flag"]
                    if book_fail:
                        self.lg.log('Retrieval of order book failed, try again next cycle')
                    else:
                        new_ord_book = book_get["ord_book"]
                        pair_newask = float(new_ord_book['asks'][0][0])
                        pair_ask_quant = float(new_ord_book['asks'][0][1])
                        pair_secondask = float(new_ord_book['asks'][1][0])

                        if pair_newask < self.t_1_price:
                            new_return = self.t_2_price / self.t_3_price * pair_newask
                            self.lg.log("Price moved down, new return calculated as " + str(new_return))
                            if new_return > self.base_rate and t_1_remaining * self.t_1_price > self.t_1_min_val:
                                self.lg.log("Replacing order " + str(self.t_1_orderID))
                                self.ord_cancel(self.pair_1, self.t_1_orderID)
                                t_1_stat_get = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)
                                self.t_1_status = t_1_stat_get["status"]
                                new_remaining = t_1_stat_get["remaining"]
                                self.lg.log(
                                    'Final status for order ' + str(self.t_1_orderID) + ' was ' + self.t_1_status)
                                if new_remaining * self.t_1_price > self.t_1_min_val \
                                        and self.t_1_status != 'FILLED':
                                    new_price = pair_newask - self.pair_1_pip
                                    new_t_1 = self.place_order_retry(self.pair_1, self.quant_str_trim(new_remaining,
                                                                                                      self.t_1_decimal),
                                                                     self.t_1_price_form.format(new_price), 'sell')
                                    stat_check = new_t_1["status"]
                                    if stat_check != 'not_placed':
                                        self.t_1_orderID = new_t_1["orderID"]
                                        self.t_1_status = stat_check
                                        self.t_1_price = new_price
                                        self.lg.log('New order ID = ' + str(self.t_1_orderID))
                                    else:
                                        self.lg.log(
                                            "Replacement order failed, abort t_1 monitoring and let cycle logic proceed")
                                        self.checkpoint_t_1_complete = True
                                else:
                                    self.lg.log('Remaining amount too small to trade, let cycle logic proceed')
                                    self.checkpoint_t_1_complete = True
                        elif pair_secondask > self.t_1_price + self.pair_1_pip and pair_ask_quant == t_1_remaining:
                            self.lg.log('Second ask more than one pip higher and no matches, repositioning')
                            self.ord_cancel(self.pair_1, self.t_1_orderID)
                            t_1_stat_get = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)
                            self.t_1_status = t_1_stat_get["status"]
                            new_remaining = t_1_stat_get["remaining"]
                            self.lg.log('Final status for order ' + str(self.t_1_orderID) + ' was ' + self.t_1_status)
                            if new_remaining * self.t_1_price > self.t_1_min_val \
                                    and self.t_1_status != 'FILLED':
                                new_price = pair_secondask - self.pair_1_pip
                                new_t_1 = self.place_order_retry(self.pair_1,
                                                                 self.quant_str_trim(new_remaining, self.t_1_decimal),
                                                                 self.t_1_price_form.format(new_price), 'sell')
                                stat_check = new_t_1["status"]
                                if stat_check != 'not_placed':
                                    self.t_1_orderID = new_t_1["orderID"]
                                    self.t_1_status = stat_check
                                    self.t_1_price = new_price
                                    self.lg.log('New order ID = ' + str(self.t_1_orderID))
                                else:
                                    self.lg.log(
                                        "Replacement order failed, abort t_1 monitoring and let cycle logic proceed")
                                    self.checkpoint_t_1_complete = True
                            else:
                                self.lg.log('Remaining amount too small to trade, let cycle logic proceed')
                                self.checkpoint_t_1_complete = True
        else:
            # double check status of t_1
            t_1_stat_get = self.get_order_stat_rem_stubborn(self.pair_1, self.t_1_orderID)
            self.t_1_status = t_1_stat_get["status"]
            self.t_1_executed = t_1_stat_get["executed"]
            coin_2_returned = self.t_1_executed * self.t_1_price
            if self.t_2_status == 'FILLED' or (coin_2_returned >= self.t_2_min_amt and coin_2_returned * self.t_2_price > self.t_2_min_val):
                self.checkpoint_t_1_complete = True
                self.cycle_count = 0
            elif self.no_bites:
                self.cyc_status = 'no_bites'
            else:
                self.checkpoint_t_1_complete = True
                self.cycle_count = 0

    def place_t_2(self):

        coin_2_bal = -1
        while coin_2_bal == -1:
            balances = self.get_bals()
            for b in balances:
                if b['asset'] == self.coin_2:
                    coin_2_bal = float(b['free'])
            if coin_2_bal == -1:
                time.sleep(1)

        self.t_1_executed = self.get_order_stat_remaining(self.pair_1, self.t_1_orderID)["executed"]
        coin_2_returned = self.t_1_executed * self.t_1_price

        if self.cancelled_partial:
            fails_needed = 1
        else:
            fails_needed = 3

        if self.t_2_status == 'not_placed' and self.t_2_fail_count < fails_needed:
            if coin_2_bal >= coin_2_returned and coin_2_returned > self.t_2_min_amt and coin_2_returned * self.t_2_price > self.t_2_min_val:
                    if self.coin_2 == 'BNB':
                        if coin_2_bal - self.target_BNB_bal > coin_2_returned:
                            self.t_2_quant = coin_2_bal - self.target_BNB_bal
                        else:
                            self.t_2_quant = coin_2_returned
                    elif self.coin_2 == 'ETH':
                        self.t_2_quant = coin_2_bal
                    else:
                        self.t_2_quant = coin_2_returned
                    t_2 = self.place_order_retry(self.pair_2, self.quant_str_trim(self.t_2_quant, self.t_2_decimal),
                                                 self.t_2_price_form.format(self.t_2_price),
                                                 'sell')
                    stat_check = t_2["status"]
                    if stat_check != 'not_placed':
                        self.t_2_orderID = t_2["orderID"]
                        self.t_2_status = stat_check
                        self.t_2_orig_price = float(self.t_2_price_form.format(self.t_2_price))
                        self.t_2_price = self.t_2_orig_price
                        self.lg.log('Initial t_2 order ID = ' + str(self.t_2_orderID))
                        self.lg.log('First retreived t_2 status = ' + self.t_2_status)
                    else:
                        self.lg.log('t_2 order failed, will try again')
                        self.t_2_fail_count += 1
            else:
                self.lg.log('Not enough ' + self.coin_2 + ' to cycle, retry')
                self.t_2_fail_count += 1
        elif self.t_2_status != 'not_placed':
            self.checkpoint_t_2_placed = True
        elif self.t_2_fail_count >= fails_needed:
            self.lg.log('Tried t_2 designated times and failed')
            self.cycle_fail = True


    def t_2_watch(self):
        if (self.t_2_status == 'NEW' or self.t_2_status == 'PARTIALLY_FILLED'):
            t_2_stat_get = self.get_order_stat_rem_stubborn(self.pair_2, self.t_2_orderID)
            self.cycle_count += 1
            self.t_2_status = t_2_stat_get["status"]
            t_2_remaining = t_2_stat_get["remaining"]

            if self.t_2_status == 'FILLED':
                self.checkpoint_t_2_complete = True
            elif self.cycle_count >= self.update_interval:
                self.cycle_count = 0
                if not self.t_2_stoploss and not self.t_2_reversal:
                    book_get = self.get_ord_book(self.pair_2)
                    book_fail = book_get["fail_flag"]
                    if book_fail:
                        self.lg.log('Retrieval of order book failed, try again next cycle')
                    else:
                        new_ord_book = book_get["ord_book"]
                        pair_newask = float(new_ord_book['asks'][0][0])
                        pair_ask_quant = float(new_ord_book['asks'][0][1])
                        pair_secondask = float(new_ord_book['asks'][1][0])
                        pair_newbid = float(new_ord_book['bids'][0][0])

                        p1_book_get = self.get_ord_book(self.pair_1)
                        new_p1_book = p1_book_get["ord_book"]
                        p1_newask = float(new_p1_book['asks'][0][0])

                        p3_book_get = self.get_ord_book(self.pair_3)
                        new_p3_book = p3_book_get["ord_book"]
                        p3_newask = float(new_p3_book['asks'][0][0])

                        fullroute_loss = (1 - pair_newbid / self.t_2_orig_price) + (
                                1 - self.t_3_price / p3_newask) + 0.00075  # static value for fee

                        # if pair_newbid < self.t_2_orig_price * self.t_2_stop_trigger:
                        if fullroute_loss > self.t_2_loss_rate_trig:
                            self.lg.log('t_2 stoploss triggered')
                            self.ord_cancel(self.pair_2, self.t_2_orderID)
                            t_2_stat_get = self.get_order_stat_remaining(self.pair_2, self.t_2_orderID)
                            self.t_2_status = t_2_stat_get["status"]
                            new_remaining = t_2_stat_get["remaining"]

                            backtrade_loss = 1 - self.t_1_price / p1_newask

                            self.lg.log('Full route loss would be ' + str(fullroute_loss)[:4])
                            self.lg.log('Backtrade loss would be ' + str(backtrade_loss)[:4])

                            # p3_book_get = self.get_ord_book(self.pair_3)
                            # new_p3_book = p3_book_get["ord_book"]
                            # p3_newask = float(new_p3_book['asks'][0][0])
                            #
                            # fullroute_loss = (1 - pair_newbid / self.t_2_orig_price) + (
                            #             1 - self.t_3_price / p3_newask) + 0.00075  # static value for fee
                            # backtrade_loss = 1 - self.t_1_price / p1_newask

                            # self.lg.log('Full route loss would be ' + str(fullroute_loss)[:4])
                            # self.lg.log('Backtrade loss would be ' + str(backtrade_loss)[:4])

                            # This should check if the loss is less bad converting straight back to XLM
                            if backtrade_loss <= fullroute_loss:
                                self.lg.log('Backtrade is less bad than going through coin_3')
                                if new_remaining >= self.t_1_min_val:
                                    backtrade_price = p1_newask * self.t_2_backstop_price
                                    backtrade_quant = new_remaining / backtrade_price
                                    new_t_2 = self.place_order_retry(self.pair_1, self.quant_str_trim(backtrade_quant,
                                                                                                      self.t_1_decimal),
                                                                     self.t_1_price_form.format(backtrade_price), 'buy')
                                    stat_check = new_t_2["status"]
                                    if stat_check != 'not_placed':
                                        self.t_2_orderID = new_t_2["orderID"]
                                        self.t_2_status = stat_check
                                        self.t_2_price = backtrade_price
                                        self.t_2_stoploss = True
                                        self.t_2_backtraded = True
                                        self.lg.log('Order ID for t_2 backtrade = ' + str(self.t_2_orderID))
                                else:
                                    self.lg.log('Coin_2 quant too small for backtrade stoploss, abort')
                                    self.cycle_fail = True
                            elif fullroute_loss < backtrade_loss:
                                self.lg.log('Going through coin_3 is less bad than backtrade')
                                stoploss_price = self.t_2_orig_price * self.t_2_stop_price
                                if new_remaining * stoploss_price > self.t_2_min_val:
                                    new_t_2 = self.place_order_retry(self.pair_2, self.quant_str_trim(new_remaining,
                                                                                                      self.t_2_decimal),
                                                                     self.t_2_price_form.format(stoploss_price), 'sell')
                                    stat_check = new_t_2["status"]
                                    if stat_check != 'not_placed':
                                        self.t_2_orderID = new_t_2["orderID"]
                                        self.t_2_status = stat_check
                                        self.t_2_price = stoploss_price
                                        self.t_2_stoploss = True
                                        self.lg.log('New order ID = ' + str(self.t_2_orderID))
                                else:
                                    self.lg.log('Coin_2 quant too small for full route stoploss, abort')
                                    self.cycle_fail = True
                        elif p1_newask < self.t_1_price * self.t_2_reverse_trigger:
                            self.t_2_reversal = True
                            self.lg.log('t_2 reversal triggered')
                            self.ord_cancel(self.pair_2, self.t_2_orderID)
                            t_2_stat_get = self.get_order_stat_remaining(self.pair_2, self.t_2_orderID)
                            self.t_2_status = t_2_stat_get["status"]
                            new_remaining = t_2_stat_get["remaining"]
                            if new_remaining > self.t_1_min_val:
                                reversal_price = self.t_1_price * self.t_2_reverse_price
                                reversal_quant = new_remaining / reversal_price
                                new_t_2 = self.place_order_retry(self.pair_1,
                                                                 self.quant_str_trim(reversal_quant, self.t_1_decimal),
                                                                 self.t_1_price_form.format(reversal_price), 'buy')
                                stat_check = new_t_2["status"]
                                if stat_check != 'not_placed':
                                    self.t_2_orderID = new_t_2["orderID"]
                                    self.t_2_status = stat_check
                                    self.t_2_price = reversal_price
                                    self.t_2_backtraded = True
                                    self.lg.log('Order ID for t_2 reversal = ' + str(self.t_2_orderID))
                            else:
                                self.lg.log('Coin_2 quant too small for reversal, abort')
                                self.cycle_fail = True
                        elif pair_newask < self.t_2_price:
                            new_return = pair_newask / self.t_3_price * self.t_1_price
                            self.lg.log("Price moved down, new return calculated as " + str(new_return))
                            if new_return > self.base_rate and t_2_remaining * self.t_2_price > self.t_2_min_val:
                                self.lg.log("Replacing order " + str(self.t_2_orderID))
                                self.ord_cancel(self.pair_2, self.t_2_orderID)
                                t_2_stat_get = self.get_order_stat_rem_stubborn(self.pair_2, self.t_2_orderID)
                                self.t_2_status = t_2_stat_get["status"]
                                new_remaining = t_2_stat_get["remaining"]
                                self.lg.log(
                                    'Final status for order ' + str(self.t_2_orderID) + ' was ' + self.t_2_status)
                                if new_remaining * (pair_newask - self.pair_2_pip) > self.t_2_min_val \
                                        and self.t_2_status != 'FILLED':
                                    new_price = pair_newask - self.pair_2_pip
                                    new_t_2 = self.place_order_retry(self.pair_2, self.quant_str_trim(new_remaining,
                                                                                                      self.t_2_decimal),
                                                                     self.t_2_price_form.format(new_price), 'sell')
                                    stat_check = new_t_2["status"]
                                    if stat_check != 'not_placed':
                                        self.t_2_orderID = new_t_2["orderID"]
                                        self.t_2_status = stat_check
                                        self.t_2_price = new_price
                                        self.lg.log('New order ID = ' + str(self.t_2_orderID))
                                    else:
                                        self.lg.log("Replacement order failed, try again next cycle")
                                else:
                                    self.lg.log('Remaining amount too small to move, hold on existing price')
                        elif pair_secondask > self.t_2_price + self.pair_2_pip and pair_ask_quant == t_2_remaining:
                            self.lg.log('Second ask more than one pip higher and no matches, assessing for reposition')
                            t_2_stat_get = self.get_order_stat_rem_stubborn(self.pair_2, self.t_2_orderID)
                            self.t_2_status = t_2_stat_get["status"]
                            new_remaining = t_2_stat_get["remaining"]
                            if new_remaining * (pair_secondask - self.pair_2_pip) > self.t_2_min_val \
                                    and self.t_2_status != 'FILLED':
                                self.ord_cancel(self.pair_2, self.t_2_orderID)
                                t_2_stat_get = self.get_order_stat_rem_stubborn(self.pair_2, self.t_2_orderID)
                                self.t_2_status = t_2_stat_get["status"]
                                self.lg.log(
                                    'Final status for order ' + str(self.t_2_orderID) + ' was ' + self.t_2_status)
                                new_price = pair_secondask - self.pair_2_pip
                                new_t_2 = self.place_order_retry(self.pair_2, self.quant_str_trim(new_remaining,
                                                                                                  self.t_2_decimal),
                                                                 self.t_2_price_form.format(new_price), 'sell')
                                stat_check = new_t_2["status"]
                                if stat_check != 'not_placed':
                                    self.t_2_orderID = new_t_2["orderID"]
                                    self.t_2_status = stat_check
                                    self.t_2_price = new_price
                                    self.lg.log('New order ID = ' + str(self.t_2_orderID))
                                else:
                                    self.lg.log("Replacement order failed, try again next cycle")
                            else:
                                self.lg.log('Remaining amount too small to move, hold on existing price')
        else:
            self.checkpoint_t_2_complete = True


    def place_t_3(self):
        coin_3_bal = -1
        while coin_3_bal == -1:
            balances = self.get_bals()
            for b in balances:
                if b['asset'] == self.coin_3:
                    coin_3_bal = float(b['free'])
            if coin_3_bal == -1:
                time.sleep(1)

        self.t_2_executed = self.get_order_stat_remaining(self.pair_2, self.t_2_orderID)["executed"]
        coin_3_returned = self.t_2_executed * self.t_2_price

        if self.t_2_stoploss:
            self.t_3_price = self.t_3_price * self.t_3_stop_price
            self.t_3_stop_trigger = 1
            self.lg.log('t_2 went to stoploss, continuing stoploss chain')

        if self.t_3_status == 'not_placed' and self.t_3_fail_count < 5 and not self.t_2_backtraded:
            if coin_3_bal >= coin_3_returned > self.t_3_min_val:
                if coin_3_bal - self.target_BTC_bal > coin_3_returned:
                    self.t_3_quant = (coin_3_bal - self.target_BTC_bal) / self.t_3_price
                else:
                    self.t_3_quant = coin_3_returned / self.t_3_price
                t_3 = self.place_order_retry(self.pair_3, self.quant_str_trim(self.t_3_quant, self.t_3_decimal),
                                             self.t_3_price_form.format(self.t_3_price),
                                             'buy')
                stat_check = t_3["status"]
                self.lg.log(stat_check)
                if stat_check != 'not_placed':
                    self.t_3_orderID = t_3["orderID"]
                    self.t_3_status = stat_check
                    self.t_3_orig_price = float(self.t_3_price_form.format(self.t_3_price))
                    self.t_3_price = self.t_3_orig_price
                    self.lg.log('Initial t_3 order ID = ' + str(self.t_3_orderID))
                    self.lg.log('First retreived t_3 status = ' + self.t_3_status)
                else:
                    self.lg.log('t_3 order failed, will try again')
                    self.t_3_fail_count += 1
            else:
                self.lg.log('Not enough ' + self.coin_3 + ' to cycle, retry')
                self.t_3_fail_count += 1
        elif self.t_3_status != 'not_placed':
            self.checkpoint_t_3_placed = True
        elif self.t_3_fail_count >= 5:
            self.lg.log('Tried t_3 five times and failed')
            self.cycle_fail = True


    def t_3_watch(self):
        if (self.t_3_status == 'NEW' or self.t_3_status == 'PARTIALLY_FILLED'):
            t_3_stat_get = self.get_order_stat_rem_stubborn(self.pair_3, self.t_3_orderID)
            self.cycle_count += 1
            self.t_3_status = t_3_stat_get["status"]
            t_3_remaining = t_3_stat_get["remaining"]

            if self.t_3_status == 'FILLED':
                self.checkpoint_t_3_complete = True
                self.cycle_count = 0
            elif self.cycle_count >= self.update_interval:
                self.cycle_count = 0
                if not self.t_3_stoploss:
                    book_get = self.get_ord_book(self.pair_3)
                    book_fail = book_get["fail_flag"]
                    if book_fail:
                        self.lg.log('Retrieval of order book failed, try again next cycle')
                    else:
                        new_ord_book = book_get["ord_book"]
                        pair_newbid = float(new_ord_book['bids'][0][0])
                        pair_bid_quant = float(new_ord_book['bids'][0][1])
                        pair_secondbid = float(new_ord_book['bids'][1][0])
                        pair_newask = float(new_ord_book['asks'][0][0])

                        if pair_newask > self.t_3_orig_price * self.t_3_stop_trigger:
                            self.lg.log('t_3 stoploss triggered')
                            self.ord_cancel(self.pair_3, self.t_3_orderID)
                            time.sleep(.5)
                            coin_3_bal = -1
                            while coin_3_bal == -1:
                                balances = self.get_bals()
                                for b in balances:
                                    if b['asset'] == self.coin_3:
                                        coin_3_bal = float(b['free'])
                                if coin_3_bal == -1:
                                    time.sleep(1)
                            stoploss_price = self.t_3_orig_price * self.t_3_stop_price
                            if coin_3_bal < self.t_3_min_val:
                                self.lg.log('Coin_3 bal too small to stoploss, abort')
                                self.cycle_fail = True
                            else:
                                if coin_3_bal > t_3_remaining * stoploss_price > self.t_3_min_val:
                                    stoploss_quant = t_3_remaining
                                else:
                                    stoploss_quant = coin_3_bal / stoploss_price
                                new_t_3 = self.place_order_retry(self.pair_3,
                                                                 self.quant_str_trim(stoploss_quant, self.t_3_decimal),
                                                                 self.t_3_price_form.format(stoploss_price), 'buy')
                                stat_check = new_t_3["status"]
                                if stat_check != "not_placed":
                                    self.t_3_orderID = new_t_3["orderID"]
                                    self.t_3_status = stat_check
                                    self.t_3_price = stoploss_price
                                    t_3_stoploss = True
                                    self.lg.log('OrderId for t_3 stoploss = ' + str(self.t_3_orderID))

                        elif pair_newbid > self.t_3_price:
                            new_return = self.t_2_price / pair_newbid * self.t_1_price
                            self.lg.log("Price moved up, new return calculated as " + str(new_return))
                            if new_return > self.base_rate and t_3_remaining * pair_newbid > self.t_3_min_val:
                                self.lg.log("Replacing order " + str(self.t_3_orderID))
                                self.ord_cancel(self.pair_3, self.t_3_orderID)
                                t_3_stat_get = self.get_order_stat_rem_stubborn(self.pair_3, self.t_3_orderID)
                                self.t_3_status = t_3_stat_get["status"]
                                new_remaining = t_3_stat_get["remaining"]
                                self.lg.log(
                                    'Final status for order ' + str(self.t_3_orderID) + ' was ' + self.t_3_status)
                                if new_remaining * (pair_newbid + self.pair_3_pip) > self.t_3_min_val \
                                        and self.t_3_status != 'FILLED':
                                    new_price = pair_newbid + self.pair_3_pip
                                    new_t_3 = self.place_order_retry(self.pair_3,
                                                                     self.quant_str_trim(new_remaining,
                                                                                         self.t_3_decimal),
                                                                     self.t_3_price_form.format(new_price), 'buy')
                                    stat_check = new_t_3["status"]
                                    if stat_check != 'not_placed':
                                        self.t_3_orderID = new_t_3["orderID"]
                                        self.t_3_status = stat_check
                                        self.t_3_price = new_price
                                        self.lg.log('New order ID = ' + str(self.t_3_orderID))
                                    else:
                                        self.lg.log("Replacement order failed, try again next cycle")
                                else:
                                    self.lg.log('Remaining amount too small to move, hold on existing price')
                        elif pair_secondbid < self.t_3_price - self.pair_3_pip and pair_bid_quant == t_3_remaining:
                            self.lg.log('Second bid more than one pip lower and no matches, assessing for reposition')
                            t_3_stat_get = self.get_order_stat_rem_stubborn(self.pair_3, self.t_3_orderID)
                            self.t_3_status = t_3_stat_get["status"]
                            new_remaining = t_3_stat_get["remaining"]
                            if new_remaining * (pair_secondbid + self.pair_3_pip) > self.t_3_min_val \
                                    and self.t_3_status != 'FILLED':
                                self.lg.log("Replacing order " + str(self.t_3_orderID))
                                self.ord_cancel(self.pair_3, self.t_3_orderID)
                                t_3_stat_get = self.get_order_stat_rem_stubborn(self.pair_3, self.t_3_orderID)
                                self.t_3_status = t_3_stat_get["status"]
                                self.lg.log(
                                    'Final status for order ' + str(self.t_3_orderID) + ' was ' + self.t_3_status)
                                new_price = pair_secondbid + self.pair_3_pip
                                new_t_3 = self.place_order_retry(self.pair_3,
                                                                 self.quant_str_trim(new_remaining, self.t_3_decimal),
                                                                 self.t_3_price_form.format(new_price), 'buy')
                                stat_check = new_t_3["status"]
                                if stat_check != 'not_placed':
                                    self.t_3_orderID = new_t_3["orderID"]
                                    self.t_3_status = stat_check
                                    self.t_3_price = new_price
                                    self.lg.log('New order ID = ' + str(self.t_3_orderID))
                                else:
                                    self.lg.log("Replacement order failed, try again next cycle")
                            else:
                                self.lg.log('Remaining amount too small to move, hold on existing price')
        else:
            self.checkpoint_t_3_complete = True
            self.cycle_count = 0

    def setfile(self, log_file):
        self.lg.set_file(log_file)

    def place_order_onetry(self, pair, quant, price, side, test=False):
        status = 'not_placed'
        orderID = '0'
        trade = {}

        if test:
            self.lg.log('Would have placed order as: pair = ' + pair + ', quant = ' + str(quant) + ', price = '
                        + str(price) + ', side = ' + side)
            status = 'was_tested'
        elif not test:
            self.lg.log('Placing order as pair = ' + pair + ', quant = ' + str(quant) + ', price = '
                        + str(price) + ', side = ' + side)
            try:
                if side == 'sell':
                    trade = client.newLimitSellOrder(pair, quant, price)
                elif side == 'buy':
                    trade = client.newLimitBuyOrder(pair, quant, price)
            except MalformedRequest as e:
                self.lg.log(
                    str(e) + ' ' + str(e.__traceback__) + ' Tried to place order as pair = ' + pair + ', quant = '
                    + str(quant) + ', price = ' + str(price) + ', side = ' + side)
                client.set_offset()
            except StatusUnknown as e:
                self.lg.log(
                    str(e) + ' ' + str(e.__traceback__) + 'API returned StatusUnknown, checking for placed order')
                order = self.check_for_open(pair)
                fail = order["fail_flag"]
                if not fail:
                    orderID = order["order_ID"]
                    status = order["status"]
            except (InternalError, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(
                    str(e) + ' ' + str(e.__traceback__) + " Some sort of connection or internal error occured")
            else:
                status = trade["status"]
                orderID = trade["orderId"]
        self.lg.log('Returning: orderID = ' + str(orderID) + ', status = ' + status)
        return {"orderID": orderID, "status": status}

    def place_order_retry(self, pair, quant, price, side, test=False):
        status = 'not_placed'
        orderID = '0'
        trade = {}
        fail_count = 0

        if test:
            self.lg.log('Would have placed order as: pair = ' + pair + ', quant = ' + str(quant) + ', price = '
                        + str(price) + ', side = ' + side)
            status = 'was_tested'
        elif not test:
            self.lg.log('Placing order as pair = ' + pair + ', quant = ' + str(quant) + ', price = '
                        + str(price) + ', side = ' + side)
            try:
                while status == 'not_placed' and fail_count < 5:
                    if side == 'sell':
                        trade = client.newLimitSellOrder(pair, quant, price)
                    elif side == 'buy':
                        trade = client.newLimitBuyOrder(pair, quant, price)
                    status = trade["status"]
                    orderID = trade["orderId"]
            except MalformedRequest as e:
                self.lg.log(
                    str(e) + ' ' + str(e.__traceback__) + ' Tried to place order as pair = ' + pair + ', quant = '
                    + str(quant) + ', price = ' + str(price) + ', side = ' + side)
                fail_count += 1
                time.sleep(1)
                client.set_offset()
            except StatusUnknown as e:
                self.lg.log(
                    str(e) + ' ' + str(e.__traceback__) + ' API returned StatusUnknown, checking for placed order')
                order = self.check_for_open(pair)
                fail = order["fail_flag"]
                if not fail:
                    orderID = order["order_ID"]
                    status = order["status"]
                elif fail:
                    fail_count += 1
                    time.sleep(1)
            except (InternalError, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(
                    str(e) + ' ' + str(e.__traceback__) + " Some sort of connection or internal error occured")
                fail_count += 1
                time.sleep(1)
            # else:
            #     status = trade["status"]
            #     orderID = trade["orderId"]
            finally:
                if fail_count >= 5:
                    self.lg.log("Retried order 5 times, still didn't take")
        self.lg.log('Returning: orderID = ' + str(orderID) + ', status = ' + status)
        return {"orderID": orderID, "status": status}

    def check_for_open(self, pair):
        self.lg.log("Attempted order may have failed checking whether it was placed")
        fail_flag = False
        mult_orders = False
        order_ID = '0'
        status = 'not_placed'
        match_amt = -1
        ord_found = False

        if pair == self.pair_1:
            match_amt = self.t_1_quant
        elif pair == self.pair_2:
            match_amt = self.t_2_quant
        elif pair == self.pair_3:
            match_amt = self.t_3_quant

        cur_open = self.get_open_ords(pair)
        num_open = 0
        for o in cur_open:
            num_open += 1

        if num_open >= 1:
            self.lg.log("At least one order is open, trying to find the right one")
            for o in cur_open:
                quant_compare = float(o["origQty"])
                if quant_compare == match_amt:
                    order_ID = o["orderId"]
                    status = o["status"]
                    ord_found = True
            if not ord_found:
                fail_flag = True
        elif num_open == 0:
            self.lg.log("No order was placed")
            fail_flag = True

        return {"order_ID": order_ID, "status": status, "fail_flag": fail_flag, "mult_orders": mult_orders}

    def get_order_stat_remaining(self, pair, Order_id):
        error_count = 0
        info_returned = False
        status = 'not_found'
        remaining = -1
        executed = -1
        fail = False

        if Order_id == 0:
            self.lg.log("Tried to check an unplaced order")
            fail = True

        while info_returned == False and not fail:
            try:
                stat_get = client.queryOrder(pair, orderId=Order_id)
            except MalformedRequest as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__) +
                            ' Order ID not found on status + remain check, keep trying')
                error_count += 1
                time.sleep(5)
                client.set_offset()
            except (
            InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                error_count += 1
                time.sleep(1)
            else:
                status = stat_get['status']
                remaining = float(stat_get['origQty']) - float(stat_get['executedQty'])
                executed = float(stat_get['executedQty'])
                info_returned = True
            finally:
                if error_count >= 5:
                    self.lg.log("Tried to get status/remaining 5 times and failed")
                    fail = True

        # self.lg.log('Returning: status = ' + status + ' remaining = ' + str(remaining))
        return {"status": status, "remaining": remaining, "executed": executed, "fail_flag": fail}

    def get_order_stat_rem_stubborn(self, pair, Order_id):
        updated = False
        status = 'not_found'
        remaining = -1
        executed = -1

        while not updated:
            if Order_id == 0:
                self.lg.log("Tried to check and unplaced order")
                updated = True
            else:
                stat_get = self.get_order_stat_remaining(pair, Order_id)
                fail = stat_get["fail_flag"]
                if not fail:
                    status = stat_get["status"]
                    remaining = stat_get["remaining"]
                    executed = stat_get['executed']
                    updated = True

        # self.lg.log('Returning: status = ' + status + ' remaining = ' + str(remaining))
        return {"status": status, "remaining": remaining, "executed": executed}

    def ord_cancel(self, pair, Order_id):
        ord_cancelled = False
        error_count = 0
        self.lg.log('Cancelling order ' + str(Order_id))
        while not ord_cancelled and error_count < 10:
            try:
                client.deleteOrder(pair, orderId=Order_id)
            except MalformedRequest as e:
                self.lg.log(str(e) + ' ' + str(
                    e.__traceback__) + ' ' + 'Order ID not found on cancel, try cancelling all open orders for the pair')
                client.set_offset()
                cur_open = self.get_open_ords(pair)
                if cur_open == []:
                    self.lg.log('Could not find the order, but no order open for the pair so must be cancelled')
                    ord_cancelled = True
                else:
                    for o in cur_open:
                        try:
                            client.deleteOrder(pair, orderId=o['orderId'])
                        except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected,
                                ProtocolError, HTTPException) as e:
                            self.lg.log(str(e) + ' ' + str(
                                e.__traceback__) + ' ' + 'Trying to cancel open orders after single cancel fails, wtf')
                            client.set_offset()
                    ord_cancelled = True
                error_count += 1
                time.sleep(1)
            except (
            InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(
                    e.__traceback__) + 'Internal or Unknown error while cancelling order, keep trying')
                error_count += 1
                time.sleep(1)
            else:
                ord_cancelled = True
            finally:
                if error_count >= 10:
                    self.lg.log('Order cancel failed 10 times, Order ID was: ' + str(Order_id))

    def get_ord_book(self, pair):
        error_count = 0
        book_returned = False
        ord_book = {}
        fail = False
        self.lg.log('Getting order book for pair ' + pair)

        while not book_returned and not fail:
            try:
                ord_book = client.depth(pair, limit=5)
            except (MalformedRequest, InternalError, StatusUnknown,
                    ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__) + ' ' + 'Order book retrieve for ' + pair +
                            ' failed, keep trying')
                error_count += 1
                time.sleep(1)
                client.set_offset()
            else:
                book_returned = True
            finally:
                if error_count >= 5:
                    self.lg.log("Tried to get order book 5 times and failed")
                    fail = True
        return {"ord_book": ord_book, "fail_flag": fail}

    def get_bals(self):
        error_count = 0
        bals_returned = False
        bals = {}
        self.lg.log('Getting balances')
        while not bals_returned and error_count < 10:
            try:
                bals = client.account()['balances']
            except (
            MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError,
            HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__) + ' ' + 'Account data request failed, keep trying')
                error_count += 1
                time.sleep(1)
                client.set_offset()
            else:
                bals_returned = True
            finally:
                if error_count >= 10:
                    self.lg.log('Balance check failed 10 times')
        return bals

    def get_open_ords(self, pair):
        error_count = 0
        got_ords = False
        open_ords = {}
        # self.lg.log('Getting open orders for pair ' + pair)
        while not got_ords and error_count < 10:
            try:
                open_ords = client.openOrders(pair)
            except (
            MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError,
            HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__) + ' ' + 'Open order request failed try again')
                error_count += 1
                time.sleep(1)
                client.set_offset()
            else:
                got_ords = True
            finally:
                if error_count >= 10:
                    self.lg.log('Open orders check failed 10 times')
        return open_ords

    def quant_str_trim(self, quant, to_decimal):
        if to_decimal == 0:
            if 0 < quant < 10:
                trimmed = str(quant)[:to_decimal + 1]
            elif 10 <= quant < 100:
                trimmed = str(quant)[:to_decimal + 2]
            elif 100 <= quant < 1000:
                trimmed = str(quant)[:to_decimal + 3]
            elif 1000 <= quant < 10000:
                trimmed = str(quant)[:to_decimal + 4]
            else:
                trimmed = 0
                self.lg.log('Quant was out of usable range, setting to 0 to prevent trade')
        else:
            if 0 < quant < 10:
                trimmed = str(quant)[:to_decimal + 2]
            elif 10 <= quant < 100:
                trimmed = str(quant)[:to_decimal + 3]
            elif 100 <= quant < 1000:
                trimmed = str(quant)[:to_decimal + 4]
            elif 1000 <= quant < 10000:
                trimmed = str(quant)[:to_decimal + 5]
            else:
                trimmed = 0
                self.lg.log('Quant was out of usable range, setting to 0 to prevent trade')

        return trimmed
