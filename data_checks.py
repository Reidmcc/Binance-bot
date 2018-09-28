from api import BinanceAPI
client = BinanceAPI('[API key]','[API secret]')
from excepts import MalformedRequest, StatusUnknown, InternalError
from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError
from http.client import HTTPException
from mult_arbit import Trades
# import sys
# import time
from log import log_c

class Data_checks(object):
    def __init__(self):
        self.lg = log_c()
        self.tr = Trades()
        self.logfile = 'Default_log.txt'

    def setfile(self, log_file):
        self.lg.set_file(log_file)
        self.logfile = log_file

    def route_check_altfirst(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip, pair_3_pip):
        calc_done = False
        route_gain = -1
        bid_p1 = -1
        ask_p2 = -1
        bid_p3 = -1
        while calc_done == False:
            try:
                bid_p1 = float(client.depth(pair_1, limit = 5)['bids'][0][0])
                ask_p2 = float(client.depth(pair_2, limit = 5)['asks'][0][0])
                bid_p3 = float(client.depth(pair_3, limit = 5)['bids'][0][0])
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                route_gain = (1 / (bid_p1 + pair_1_pip)) * (ask_p2 - pair_2_pip)  / (bid_p3 + pair_3_pip)
                calc_done = True

        return (route_gain, bid_p1, ask_p2, bid_p3)


    def route_check_altlast(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip, pair_3_pip):
        calc_done = False
        route_gain = -1
        bid_p2 = -1
        ask_p3 = -1
        ask_p1 = -1
        while calc_done == False:
            try:
                ask_p1 = float(client.depth(pair_1, limit = 5)['asks'][0][0]) - float(pair_1_pip)
                bid_p2 = float(client.depth(pair_2, limit = 5)['bids'][0][0]) + float(pair_2_pip)
                ask_p3 = float(client.depth(pair_3, limit = 5)['asks'][0][0]) - float(pair_3_pip)
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                # route_gain = ((ask_p1 - pair_1_pip) / ((bid_p2 + pair_2_pip)) * (ask_p3 - pair_3_pip))
                route_gain = ask_p1  / bid_p2 * ask_p3
                calc_done = True
        return (route_gain, ask_p1, bid_p2, ask_p3)


    def route_check_altlast_take_t2(self, pair_1, pair_2, pair_3, pair_1_pip, pair_3_pip):
        calc_done = False
        route_gain = -1
        while calc_done == False:
            try:
                ask_p1 = float(client.depth(pair_1, limit = 5)['asks'][0][0])
                ask_p2 = float(client.depth(pair_2, limit = 5)['asks'][0][0])
                ask_p3 = float(client.depth(pair_3, limit = 5)['asks'][0][0])
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
            else:
                route_gain = ((ask_p1 - pair_1_pip) / ((ask_p2)) * (ask_p3 - pair_3_pip))
                calc_done = True
        return route_gain


    def route_check_altlast_take_t3(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip):
        calc_done = False
        route_gain = -1
        ask_p1 = -1
        bid_p2 = -1
        bid_p3 = -1
        p3_bid_quant = -1
        while calc_done == False:
            try:
                ask_p1 = float(client.depth(pair_1, limit = 5)['asks'][0][0])
                bid_p2 = float(client.depth(pair_2, limit = 5)['bids'][0][0])
                p3_depth = client.depth(pair_3, limit = 5)
                bid_p3 = float(p3_depth['bids'][0][0])
                p3_bid_quant = float(p3_depth['bids'][0][1])
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                route_gain = ((ask_p1 - pair_1_pip) / ((bid_p2 + pair_2_pip)) * (bid_p3))
                calc_done = True
        return (route_gain, ask_p1, bid_p2, bid_p3, p3_bid_quant)


    def route_check_altlast_take_t2_t3(self, pair_1, pair_2, pair_3, pair_1_pip):
        calc_done = False
        route_gain = -1
        while calc_done == False:
            try:
                ask_p1 = float(client.depth(pair_1, limit = 5)['asks'][0][0])
                ask_p2 = float(client.depth(pair_2, limit = 5)['asks'][0][0])
                bid_p3 = float(client.depth(pair_3, limit = 5)['bids'][0][0])
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                route_gain = (ask_p1 - pair_1_pip) / ask_p2 * bid_p3
                calc_done = True
        return route_gain


    def get_low_ask(self, pair):
        ask = -1
        got_ask = False
        while got_ask == False:
            try:
                ask = client.depth(pair, limit = 5)['asks'][0][0]
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                got_ask = True
        return ask


    def get_high_bid(self, pair):
        bid = -1
        got_bid = False
        while got_bid == False:
            try:
                bid = client.depth(pair, limit = 5)['bids'][0][0]
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                got_bid = True
        return bid


    def route_check_alt_last_lastprice(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip, pair_3_pip):
        route_gain = -1
        calc_done = False
        t_1_price = -1
        t_2_price = -1
        t_3_price = -1
        while calc_done == False:
            try:
                prices = client.allPrices()
                for p in prices:
                    symbol = p['symbol']
                    if symbol == pair_1:
                        t_1_price =  float(p['price'])
                    if symbol == pair_2:
                        t_2_price =  float(p['price'])
                    if symbol == pair_3:
                        t_3_price =  float(p['price'])
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                route_gain = (t_1_price / (t_2_price) * t_3_price)
                calc_done = True

        return route_gain


    def route_check_t3_ask_oth_lastprice(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip, pair_3_pip):
        route_gain = -1
        ask_p3 = -1
        calc_done = False
        t_1_price = -1
        t_2_price = -1
        while calc_done == False:
            try:
                prices = client.allPrices()
                for p in prices:
                    symbol = p['symbol']
                    if symbol == pair_1:
                        t_1_price = float(p['price']) - pair_1_pip
                    if symbol == pair_2:
                        t_2_price = float(p['price']) + pair_2_pip

                ask_p3 = float(client.depth(pair_3, limit=5)['asks'][0][0]) - pair_3_pip
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                route_gain = t_1_price / t_2_price * ask_p3
                calc_done = True

        return (route_gain, t_1_price, t_2_price, ask_p3)



    def route_check_altfirst_t1_bid_oth_lastprice(self, pair_1, pair_2, pair_3, pair_1_pip, pair_2_pip, pair_3_pip):
        route_gain = -1
        bid_p1 = -1
        t_2_price = -1
        t_3_price = -1
        calc_done = False
        while calc_done == False:
            try:
                prices = client.allPrices()
                for p in prices:
                    symbol = p['symbol']
                    if symbol == pair_2:
                        t_2_price = float(p['price']) + pair_2_pip
                    if symbol == pair_3:
                        t_3_price = float(p['price']) - pair_3_pip

                bid_p1 = float(client.depth(pair_1, limit = 5)['bids'][0][0])
                # ask_p2 = float(client.depth(pair_2, limit = 5)['asks'][0][0])
                # bid_p3 = float(client.depth(pair_3, limit = 5)['bids'][0][0])
            except (MalformedRequest, InternalError, StatusUnknown, ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                self.lg.log(str(e) + ' ' + str(e.__traceback__))
                client.set_offset()
            else:
                route_gain = (1 / (bid_p1 + pair_1_pip)) * (t_2_price - pair_2_pip)  / (t_3_price + pair_3_pip)
                calc_done = True

        return (route_gain, bid_p1, t_2_price, t_3_price)


    # skit_opt_ETH = dc.route_check_altfirst('XLMBNB', 'XLMETH', 'BNBETH', 1E-5, 1E-8, 1E-6)
    # print(skit_opt_ETH)
