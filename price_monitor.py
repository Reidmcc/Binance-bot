##### Market watcher for mult_arbit strategy
##### Currently hard-coded for two pair-sets

from api import BinanceAPI
client = BinanceAPI('[API key]','[API secret')
client.set_offset()
import time
# import datetime
from data_checks import Data_checks
from mult_arbit import Trades
from log import log_c


class mon:
    def __init__(self):
        self.dc = Data_checks()
        self.XLM_cyc_active = False
        self.ADA_cyc_active = False
        self.XLM_cyc_stat = 'none'
        self.ADA_cyc_stat = 'none'
        self.XLM_cyc_done = False
        self.ADA_cyc_done = False
        self.check_counter = 0
        self.t_meth = Trades()
        self.check_balances = True
        self.XLM_bal = -1
        self.ADA_bal = -1
        self.XLM_tr = Trades()
        self.ADA_tr = Trades()
        self.lg = log_c()
        self.logfile = 'Default_log.txt'
        self.active = True
        self.min_return = 1.0045

    def monitor(self):

        self.XLM_tr.setfile(self.logfile)
        self.ADA_tr.setfile(self.logfile)
        self.t_meth.setfile(self.logfile)

        while self.active:

            if self.check_balances:
                self.bal_check()
                self.check_balances = False

            if not self.XLM_cyc_active and not self.ADA_cyc_active:
                self.XLM_rate_check()
                self.ADA_rate_check()
            elif self.XLM_cyc_active and not self.ADA_cyc_active and self.check_counter >= 3:
                self.ADA_rate_check()
                self.check_counter = 0
            elif self.ADA_cyc_active and not self.XLM_cyc_active and self.check_counter >= 3:
                self.XLM_rate_check()
                self.check_counter = 0

            if self.XLM_cyc_active:
                self.XLM_tr.run_cycle()
                self.XLM_cyc_stat = self.XLM_tr.cur_stat()
                self.lg.log('Current XLM cycle status is ' + self.XLM_cyc_stat)
                self.check_counter += 1
                if self.XLM_cyc_stat == 'complete' or self.XLM_cyc_stat == 'failed' or self.XLM_cyc_stat == 'no_bites':
                    self.XLM_cyc_active = False
                    self.check_balances = True
                    self.XLM_tr = Trades()
                    self.XLM_tr.setfile(self.logfile)

            if self.ADA_cyc_active:
                self.ADA_tr.run_cycle()
                self.ADA_cyc_stat = self.ADA_tr.cur_stat()
                self.lg.log('Current ADA cycle status is ' + self.ADA_cyc_stat)
                self.check_counter += 1
                if self.ADA_cyc_stat == 'complete' or self.ADA_cyc_stat == 'failed' or self.ADA_cyc_stat == 'no_bites':
                    self.ADA_cyc_active = False
                    self.check_balances = True
                    self.ADA_tr = Trades()
                    self.ADA_tr.setfile(self.logfile)

            time.sleep(.5)


    def bal_check(self):
        self.XLM_bal = -1
        self.ADA_bal = -1
        while self.XLM_bal == -1 or self.ADA_bal == -1:
            balances = self.t_meth.get_bals()
            for b in balances:
                if b['asset'] == 'XLM':
                    self.XLM_bal = int(float(b['free']))
                elif b['asset'] == 'ADA':
                    self.ADA_bal = int(float(b['free']))
            if self.XLM_bal == -1 or self.ADA_bal == -1:
                time.sleep(1)

    def XLM_rate_check(self):

        print('----------------------------')

        ETH_back = self.dc.route_check_altlast('ETHBTC', 'XLMBTC', 'XLMETH', 1E-6, 1E-8, 1E-8)
        ETH_return = ETH_back[0]
        ETH_t_1_price = ETH_back[3]
        ETH_t_2_price = ETH_back[1]
        ETH_t_3_price = ETH_back[2]

        print("XLM-ETH-BTC return = " + "{:.5f}".format(ETH_return))

        if ETH_return >= self.min_return:
            print('XLM-ETH-BTC is good to go!')
            self.XLM_tr.set_params('XLMETH', 'ETHBTC', 'XLMBTC', 1E-8, 1E-6, 1E-8,
                           self.XLM_bal, ETH_t_1_price, ETH_t_2_price, ETH_t_3_price)
            self.XLM_cyc_active = True
            self.XLM_tr.run_cycle()
            self.XLM_cyc_stat = self.XLM_tr.cur_stat()
            self.lg.log('XLM cycle is active')
            self.check_balances = True
        else:
            print('XLM-ETH-BTC is no good.')

        print('')

        if not self.XLM_cyc_active:

            BNB_back = self.dc.route_check_altlast('BNBBTC', 'XLMBTC', 'XLMBNB', 1E-7, 1E-8, 1E-5)
            BNB_return = BNB_back[0]
            BNB_t_1_price = BNB_back[3]
            BNB_t_2_price = BNB_back[1]
            BNB_t_3_price = BNB_back[2]

            print("XLM-BNB-BTC return = " + "{:.5f}".format(BNB_return))

            if BNB_return >= self.min_return:
                print('XLM-BNB-BTC is good to go!')
                self.XLM_tr.set_params('XLMBNB', 'BNBBTC', 'XLMBTC', 1E-5, 1E-7, 1E-8,
                               self.XLM_bal, BNB_t_1_price, BNB_t_2_price, BNB_t_3_price)
                self.XLM_cyc_active = True
                self.XLM_tr.run_cycle()
                self.XLM_cyc_stat = self.XLM_tr.cur_stat()
                self.lg.log('XLM cycle is active')
                self.check_balances = True
            else:
                print('XLM-BNB-BTC is no good')

            print('')

    def ADA_rate_check(self):

        print('----------------------------')

        ADA_ETH_back = self.dc.route_check_altlast('ETHBTC', 'ADABTC', 'ADAETH', 1E-6, 1E-8, 1E-8)
        ADA_ETH_return = ADA_ETH_back[0]
        ADA_ETH_t_1_price = ADA_ETH_back[3]
        ADA_ETH_t_2_price = ADA_ETH_back[1]
        ADA_ETH_t_3_price = ADA_ETH_back[2]

        print("ADA-ETH-BTC return = " + "{:.5f}".format(ADA_ETH_return))

        if ADA_ETH_return >= self.min_return:
            print('ADA-ETH-BTC is good to go!')
            self.ADA_tr.set_params('ADAETH', 'ETHBTC', 'ADABTC', 1E-8, 1E-6, 1E-8,
                           self.ADA_bal, ADA_ETH_t_1_price, ADA_ETH_t_2_price, ADA_ETH_t_3_price)
            self.ADA_tr.run_cycle()
            self.ADA_cyc_stat = self.ADA_tr.cur_stat()
            self.ADA_cyc_active = True
            self.lg.log('ADA cycle is active')
            self.check_balances = True
        else:
            print('ADA-ETH-BTC is no good.')

        print('')

        if not self.ADA_cyc_active:

            ADA_BNB_back = self.dc.route_check_altlast('BNBBTC', 'ADABTC', 'ADABNB', 1E-7, 1E-8, 1E-5)
            ADA_BNB_return = ADA_BNB_back[0]
            ADA_BNB_t_1_price = ADA_BNB_back[3]
            ADA_BNB_t_2_price = ADA_BNB_back[1]
            ADA_BNB_t_3_price = ADA_BNB_back[2]

            print("ADA-BNB-BTC return = " + "{:.5f}".format(ADA_BNB_return))

            if ADA_BNB_return >= self.min_return:
                print('ADA-BNB-BTC is good to go!')
                self.ADA_tr.set_params('ADABNB', 'BNBBTC', 'ADABTC', 1E-5, 1E-7, 1E-8,
                               self.ADA_bal, ADA_BNB_t_1_price, ADA_BNB_t_2_price, ADA_BNB_t_3_price)
                self.ADA_cyc_active = True
                self.ADA_tr.run_cycle()
                self.ADA_cyc_stat = self.ADA_tr.cur_stat()
                self.lg.log('ADA cycle is active')
                self.check_balances = True
            else:
                print('ADA-BNB-BTC is no good')

            print('')

    def setfile(self, log_file):
        self.lg.set_file(log_file)
        self.logfile = log_file
