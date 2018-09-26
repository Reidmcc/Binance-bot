######   Inspired by the Turtle Traders from the 1980s
######   More information at http://www.tradingblox.com/originalturtles/
######   Testing suggests this strategy does NOT work well with crypto
######   This is in the middle of a refactor



from api import BinanceAPI
client = BinanceAPI('[API key]','[API secret]')
# import time
# from data_checks import Data_checks
# import pandas
# from datetime import datetime
# import matplotlib.pyplot as plt
import datetime
from excepts import MalformedRequest, StatusUnknown, InternalError
from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from http.client import HTTPException
from urllib3.exceptions import ProtocolError


class turtle:
    def __init__(self):
        self.pair = ""
        self.pip_sats = None
        self.price_mult = 1
        self.interval = None
        self.capital = None
        self.limit = None
        self.exit_trigger = None
        self.enter_trigger = None
        self.red = '\u001b[31;1m'
        self.green = '\033[92m'
        self.yellow = '\033[93m'
        self.blue = '\u001b[34m'
        self.mag = '\u001b[35;1m'
        self.stop_col = '\033[0m'


    def set_params(self, pair, interval, pip_sats, capital, limit, exit_trigger = 2, enter_trigger = 20, price_mult = 1):
        self.pair = pair
        self.pip_sats = pip_sats
        self.interval = interval
        self.capital = capital
        self.limit = limit
        self.exit_trigger = exit_trigger
        self.enter_trigger = enter_trigger
        self.price_mult = price_mult

    def find_trades(self):
        open_long = False
        open_short = False
        whip_retry_long = False
        whip_retry_short = False

        long_stop_trig = None
        long_enter_price = None
        long_size = None
        # long_exit_price = None

        short_stop_trig = None
        short_enter_price = None
        short_size = None
        # short_exit_price = None

        lost_longs = 0
        won_longs = 0
        lost_shorts = 0
        won_shorts = 0

        high_test = "high_20"
        low_test = "low_20"

        last_win = False

        worst_recorded = False
        worst_loss = None
        worst_string = ''

        best_recorded = False
        best_gain = None
        best_string = ''

        stats = self.calc_stats()

        for s in stats:

            # print('')
            # ticker = str(s["time"] + " Open: " + "{:.8f}".format(s["open"]) + " High: " + "{:.8f}".format(s["high"]) + " Low: " + "{:.8f}".format(s["low"]) + " Close: " "{:.8f}".format(s["close"]) + " N = " + "{:.8f}".format(s["N"])
            #     + " High 20: " + "{:.8f}".format(s["high_20"]) + " Low 20: " +  "{:.8f}".format(s["low_20"]))
            print(self.pair + s["time"] + " Open: " + "{:.8f}".format(s["open"]) + " High: " + "{:.8f}".format(s["high"]) + " Low: " + "{:.8f}".format(s["low"]) + " Close: " "{:.8f}".format(s["close"]) + " N = " + "{:.8f}".format(s["N"])
                + " High 20: " + "{:.8f}".format(s["high_20"]) + " Low 20: " +  "{:.8f}".format(s["low_20"]))
            if s["count"] >= self.enter_trigger + 3 \
                    and s["high_10"] != None and s["low_10"] != None \
                    and s[high_test] != None and s[low_test] != None:
                if not open_long:
                    if s["high"] > s[high_test]:# and s["close"] > s["open"]:
                        long_enter_price = s[high_test]
                        # if s["unit"] < self.capital / long_enter_price:
                        #     long_size = s["unit"]
                        # else:
                        #     long_size = self.capital / long_enter_price
                        long_size = s["unit"]
                        long_stop_trig = long_enter_price - (1 * s["N"])
                        # long_stop_trig = long_enter_price * .99
                        open_long = True
                        print(self.blue + "Fast Long Breakout:" + " Entering at " + "{:.8f}".format(long_enter_price) + " Postion size = " + "{:.2f}".format(long_size)
                            + " with stop at " + "{:.8f}".format(long_stop_trig) + self.stop_col)
                        print('')
                elif s["low"] <= long_stop_trig and not whip_retry_long:
                    loss = (long_size * .9975 * long_stop_trig * .9975)  - (long_enter_price * long_size)
                    # loss = (long_size * long_stop_trig) - (long_enter_price * long_size)
                    print(self.red  + "Long stop loss triggered at " + "{:.8f}".format(long_stop_trig) + " for loss of " + "{:.8f}".format(loss) + self.stop_col)
                    open_long = False
                    # if not last_win:
                    self.capital += loss
                    lost_longs += 1
                    print("New total capital = " + "{:.8f}".format(self.capital))
                    print('')
                    if not worst_recorded:
                        worst_loss = loss
                        worst_string = str(s["time"] + ' ' + self.red  + "Long stop loss triggered at " + "{:.8f}".format(long_stop_trig) + " for loss of " + "{:.8f}".format(loss) + self.stop_col)
                        worst_recorded = True
                    elif loss < worst_loss:
                        worst_loss = loss
                        worst_string = str(s["time"] + ' ' + self.red + "Long stop loss triggered at " + "{:.8f}".format(long_stop_trig) + " for loss of " + "{:.8f}".format(loss) + self.stop_col)
                    # last_win = False
                # elif s["low"] <= s["low_10"]:
                elif s["low"] <= s["low_10"] and s["low_10"] > long_enter_price * 1.005:
                    long_exit_price = s["low_10"]
                    prof_or_loss = (long_size * .9975 * long_exit_price * .9975)  - (long_enter_price * long_size)
                    # prof_or_loss = (long_size * long_exit_price ) - (long_enter_price * long_size)
                    open_long = False
                    # if not last_win:
                    # self.capital += prof_or_loss
                    # print("New total capital = " + "{:.8f}".format(self.capital))
                    # print('')
                    if prof_or_loss > 0:
                        color = self.green
                        won_longs += 1
                        last_win = True
                        self.capital += prof_or_loss
                    else:
                        color = self.red
                        lost_longs += 1
                        last_win = False
                        self.capital += prof_or_loss
                    print(color + "Closing Long Postion:" " Exiting at " + "{:.8f}".format(long_exit_price) + " for profit/loss of " + "{:.8f}".format(prof_or_loss) + self.stop_col)
                    print("New total capital = " + "{:.8f}".format(self.capital))
                    print('')
                    if prof_or_loss > 0:
                        if not best_recorded:
                            best_gain = prof_or_loss
                            best_string = str(s["time"] + ' ' + color + "Closing Long Postion:" " Exiting at " + "{:.8f}".format(long_exit_price) + " for profit/loss of " + "{:.8f}".format(prof_or_loss) + self.stop_col)
                            best_recorded = True
                        elif prof_or_loss > best_gain:
                            best_gain = prof_or_loss
                            best_string = str(s["time"] + ' ' + color + "Closing Long Postion:" " Exiting at " + "{:.8f}".format(long_exit_price) + " for profit/loss of " + "{:.8f}".format(prof_or_loss) + self.stop_col)


        return (self.capital, lost_longs, won_longs, lost_shorts, won_shorts, best_string, worst_string)




    def calc_stats(self):
        hist = []

        dat = self.get_klines(self.pair, self.interval, self.limit)

        count = 0
        init_range_tot = 0

        for k in dat:
            count += 1
            t_str = str(k[0])
            k_time = int(t_str[:10])
            k_t_stamp = str(datetime.datetime.fromtimestamp(k_time))
            k_open = float(k[1]) * self.price_mult
            k_high = float(k[2]) * self.price_mult
            k_low = float(k[3]) * self.price_mult
            k_close = float(k[4]) * self.price_mult

            if count == 1:
                hist.append(
                    {
                        "count":count,
                        "time":k_t_stamp,
                        "open":k_open,
                        "high":k_high,
                        "low":k_low,
                        "close":k_close,
                        "true_range":0,
                        "N":0,
                        "unit":0,
                        "high_10": 0,
                        "low_10": 0,
                        "high_20": 0,
                        "low_20": 0,
                        "high_55": 0,
                        "low_55": 0
                    }
                )
            elif count <= self.enter_trigger + 1:
                prev_c = hist[-1]["close"]
                high_min_low = k_high - k_low
                high_min_prev = k_high - prev_c
                prev_min_low = prev_c - k_low
                diff_list = (high_min_low, high_min_prev, prev_min_low)
                max_diff = max(diff_list)
                hist.append(
                    {
                        "count": count,
                        "time": k_t_stamp,
                        "open": k_open,
                        "high": k_high,
                        "low": k_low,
                        "close": k_close,
                        "true_range": max_diff,
                        "N": 0,
                        "unit":0,
                        "high_10":0,
                        "low_10":0,
                        "high_20":0,
                        "low_20":0,
                        "high_55":0,
                        "low_55":0
                    }
                )
                init_range_tot += max_diff
            elif count == self.enter_trigger + 2:
                init_avg = init_range_tot / 20
                prev_c = hist[-1]["close"]
                high_min_low = k_high - k_low
                high_min_prev = k_high - prev_c
                prev_min_low = prev_c - k_low
                diff_list = (high_min_low, high_min_prev, prev_min_low)
                max_diff = max(diff_list)
                k_N = (19 * init_avg + max_diff) / 20
                k_unit = (self.capital * .01) / k_N

                set_10 = False
                high_10 = False
                low_10 = False
                for i in range(1, self.exit_trigger):
                    if not set_10:
                        high_10 = hist[-i]["high"]
                        low_10 = hist[-i]["low"]
                        set_10 = True
                    else:
                        if hist[-i]["high"] > high_10:
                            high_10 = hist[-i]["high"]
                        if hist[-i]["low"] < low_10:
                            low_10 = hist[-i]["low"]

                set_20 = False
                high_20 = False
                low_20 = False
                for i in range(1, self.enter_trigger):
                    if not set_20:
                        high_20 = hist[-i]["high"]
                        low_20 = hist[-i]["low"]
                        set_20 = True
                    else:
                        if hist[-i]["high"] > high_20:
                            high_20 = hist[-i]["high"]
                        if hist[-i]["low"] < low_20 or low_20 == None:
                            low_20 = hist[-i]["low"]

                hist.append(
                    {
                        "count": count,
                        "time": k_t_stamp,
                        "open": k_open,
                        "high": k_high,
                        "low": k_low,
                        "close": k_close,
                        "true_range": max_diff,
                        "N": k_N,
                        "unit":k_unit,
                        "high_10":high_10,
                        "low_10":low_10,
                        "high_20": high_20,
                        "low_20": low_20,
                        "high_55": 0,
                        "low_55": 0
                    }
                )
            elif count < 56:
                prev_N = hist[-1]["N"]
                prev_c = hist[-1]["close"]
                high_min_low = k_high - k_low
                high_min_prev = k_high - prev_c
                prev_min_low = prev_c - k_low
                diff_list = (high_min_low, high_min_prev, prev_min_low)
                max_diff = max(diff_list)
                k_N = (19 * prev_N + max_diff) / 20
                k_unit = (self.capital * .01) / k_N

                set_10 = False
                high_10 = False
                low_10 = False
                for i in range(1, self.exit_trigger):
                    if not set_10:
                        high_10 = hist[-i]["high"]
                        low_10 = hist[-i]["low"]
                        set_10 = True
                    else:
                        if hist[-i]["high"] > high_10:
                            high_10 = hist[-i]["high"]
                        if hist[-i]["low"] < low_10:
                            low_10 = hist[-i]["low"]

                set_20 = False
                high_20 = False
                low_20 = False
                for i in range(1, self.enter_trigger):
                    if not set_20:
                        high_20 = hist[-i]["high"]
                        low_20 = hist[-i]["low"]
                        set_20 = True
                    else:
                        if hist[-i]["high"] > high_20:
                            high_20 = hist[-i]["high"]
                        if hist[-i]["low"] < low_20 or low_20 == None:
                            low_20 = hist[-i]["low"]

                hist.append(
                    {
                        "count": count,
                        "time": k_t_stamp,
                        "open": k_open,
                        "high": k_high,
                        "low": k_low,
                        "close": k_close,
                        "true_range": max_diff,
                        "N": k_N,
                        "unit": k_unit,
                        "high_10": high_10,
                        "low_10": low_10,
                        "high_20": high_20,
                        "low_20": low_20,
                        "high_55": 0,
                        "low_55": 0
                    }
                )
            else:
                prev_N = hist[-1]["N"]
                prev_c = hist[-1]["close"]
                high_min_low = k_high - k_low
                high_min_prev = k_high - prev_c
                prev_min_low = prev_c - k_low
                diff_list = (high_min_low, high_min_prev, prev_min_low)
                max_diff = max(diff_list)
                k_N = (19 * prev_N + max_diff) / 20
                k_unit = (self.capital * .01) / k_N

                set_10 = False
                high_10 = False
                low_10 = False
                for i in range(1, self.exit_trigger):
                    if not set_10:
                        high_10 = hist[-i]["high"]
                        low_10 = hist[-i]["low"]
                        set_10 = True
                    else:
                        if hist[-i]["high"] > high_10:
                            high_10 = hist[-i]["high"]
                        if hist[-i]["low"] < low_10:
                            low_10 = hist[-i]["low"]

                set_20 = False
                high_20 = False
                low_20 = False
                for i in range(1, self.enter_trigger):
                    if not set_20:
                        high_20 = hist[-i]["high"]
                        low_20 = hist[-i]["low"]
                        set_20 = True
                    else:
                        if hist[-i]["high"] > high_20:
                            high_20 = hist[-i]["high"]
                        if hist[-i]["low"] < low_20 or low_20 == None:
                            low_20 = hist[-i]["low"]

                set_55 = False
                high_55 = False
                low_55 = False
                for i in range(1, 55):
                    if not set_55:
                        high_55 = hist[-i]["high"]
                        low_55 = hist[-i]["low"]
                        set_55 = True
                    else:
                        if hist[-i]["high"] > high_55 or high_55 == None:
                            high_55 = hist[-i]["high"]
                        if hist[-i]["low"] < low_55 or low_55 == None:
                            low_55 = hist[-i]["low"]
                hist.append(
                    {
                        "count": count,
                        "time": k_t_stamp,
                        "open": k_open,
                        "high": k_high,
                        "low": k_low,
                        "close": k_close,
                        "true_range": max_diff,
                        "N": k_N,
                        "unit": k_unit,
                        "high_10": high_10,
                        "low_10": low_10,
                        "high_20": high_20,
                        "low_20": low_20,
                        "high_55": high_55,
                        "low_55": low_55
                    }
                )
        return hist



    def get_klines(self, pair, interval, limit):
        klines = []
        got_klines = False

        while not got_klines:
            try:
                klines = client.klines(pair, interval=interval, limit=limit)
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError,
                    HTTPException) as e:
                print(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                got_klines = True

        return klines
