##### This wrapper is https://github.com/CryptoVader/pyBinance 
##### Modified to support client/server clock drift offsetting. 
##### Binance rejects any API call that arrives with a timestamp 1000ms ahead of server time.
##### My clock runs fast, so re-offsetting is necessary. 
##### If you don't have this problem I suggest using the original (cited above)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from http.client import HTTPException
from urllib3.exceptions import ProtocolError

import hmac
import hashlib
import requests
import json
import time

from excepts import MalformedRequest, StatusUnknown, InternalError

class BinanceAPI(object):

    WEBSITE = 'https://www.binance.com'
    API_URL = 'https://www.binance.com/api/'

    def __init__(self, api_key=None, api_secret=None):

        self.key = api_key
        self.secret = api_secret
        self.session = requests.session()
        self.time_offset = 2000
        self.session.headers.update({'Accept': 'application/json',
                                    'X-MBX-APIKEY': self.key})

    def refresh_session(self):
        self.session = 'kill and refresh'
        self.session = requests.session()

    def set_offset(self):
        got_time = False
        while not got_time:
            try:
                cur_time = int(time.time() * 1000)
                bintime = int(self.time()['serverTime'])
                time_diff = cur_time - bintime
                if time_diff > 0:
                    self.time_offset = time_diff
                else:
                    self.time_offset = 500
            except (InternalError, StatusUnknown,
                        ConnectionError, RemoteDisconnected, ProtocolError, HTTPException) as e:
                print(str(e) + ' ' + str(e.__traceback__) + 'Time check failed, retry')
                time.sleep(.5)
            else:
                got_time = True

    def _sign(self, data):

        assert(self.key and self.secret)

        url_data = "&".join(['%s=%s' % (k,v) for k,v in data.items()])

        return hmac.new(bytes(self.secret, 'utf-8'), msg=url_data.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()


    def _request(self, endpoint, params, http_method):
        
        r = getattr(self.session, http_method)(BinanceAPI.API_URL + endpoint, params=params)
        
        if r.status_code == 200:
            return json.loads(r.text)

        # HTTP 504 return code is used when the API successfully sent the message but not get a response within the timeout period. 
        # It is important to NOT treat this as a failure; the execution status is UNKNOWN and could have been a success."""
        elif r.status_code == 504:
            raise StatusUnknown(r.text)

        # HTTP 5XX return codes are used for internal errors; the issue is on Binance's side.
        elif r.status_code >= 500:
            raise InternalError(r.text)

        # HTTP 4XX return codes are used for for malformed requests; the issue is on the sender's side.
        else:
            raise MalformedRequest(r.text)

        return json.loads(r.text)


    def _get(self, endpoint, param=None):
        return self._request(endpoint, param, "get")

    def _post(self, endpoint, param=None):
        return self._request(endpoint, param, "post")

    def _delete(self, endpoint, param=None):
        return self._request(endpoint, param, "delete")

    def _put(self, endpoint, param=None):
        return self._request(endpoint, param, "put")


    def set_api(self, api_key, api_secret):

        self.key = api_key
        self.secret = api_secret
        self.session.headers.update({'Accept': 'application/json',
                                    'X-MBX-APIKEY': self.key})


    # Public endpoints, unsigned
    def ping(self):
        """
        Test connectivity to the Rest API.
        GET /api/v1/ping
        """

        return self._get('v1/ping')


    def time(self):
        """
        Test connectivity to the Rest API and get the current server time.
        GET /api/v1/time
        """

        return self._get('v1/time')


    def depth(self, symbol, limit=100):
        """
        Get order book.
        GET /api/v1/depth
        """

        p = {'symbol': symbol, 'limit': limit}
        
        return self._get('v1/depth', p)


    def aggTrades(self, symbol, fromId=None, startTime=None, endTime=None, limit=500):
        """
        Get compressed, aggregate trades. Trades that fill at the time, from the same order, with the same price will have the quantity aggregated.
        GET /api/v1/aggTrades
        """

        p = {'symbol': symbol}

        if fromId:
            p['fromId'] = fromId

        if startTime:
            p['startTime'] = startTime

        if endTime:
            p['endTime'] = endTime

        # If both startTime and endTime are sent, limit should not be sent.
        if not startTime or not endTime:
            p['limit'] = limit

        return self._get('v1/aggTrades', p)


    def klines(self, symbol, interval, startTime=None, endTime=None, limit=500):
        """
        Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.
        GET /api/v1/klines
        """

        p = {'symbol': symbol, 'interval': interval}

        if startTime:
            p['startTime'] = startTime

        if endTime:
            p['endTime'] = endTime

        if limit:
            p['limit'] = limit

        return self._get('v1/klines?', p)


    def stats24hr(self, symbol):
        """
        24 hour price change statistics.
        GET /api/v1/ticker/24hr
        """

        p = {'symbol': symbol}

        return self._get('v1/ticker/24hr?', p)


    def allPrices(self):
        """
        Latest price for all symbols.
        GET /api/v1/ticker/allPrices
        """

        return self._get('v1/ticker/allPrices')


    def allBookTickers(self):
        """
        Best price/qty on the order book for all symbols.
        GET /api/v1/ticker/allBookTickers
        """

        return self._get('v1/ticker/allBookTickers')


    # Public methods that require signature
    def newLimitBuyOrder(self, symbol, quantity, price):
        return self.newOrder(symbol, "BUY", "LIMIT", "GTC", quantity, price)

    def newLimitSellOrder(self, symbol, quantity, price):
        return self.newOrder(symbol, "SELL", "LIMIT", "GTC", quantity, price)

    def newMarketBuyOrder(self, symbol, quantity, price):
        return self.newOrder(symbol, "BUY", "MARKET", "GTC", quantity, price)

    def newMarketSellOrder(self, symbol, quantity, price):
        return self.newOrder(symbol, "SELL", "MARKET", "GTC", quantity, price)


    def newOrder(self, symbol, side, type, timeInForce, quantity, price, newClientOrderId=None, stopPrice=None, icebergQty=None, recvWindow=None):
        """
        Send in a new order.
        POST /api/v3/order
        """
        
        p = {'symbol': symbol,
             'side': side,
             'type': type,
             'timeInForce': timeInForce,
              'quantity': quantity,
              'price': price,
              'timestamp': int((time.time() * 1000) - self.time_offset)}

        if newClientOrderId:
            p['newClientOrderId'] = newClientOrderId

        if stopPrice:
            p['stopPrice'] = stopPrice

        if icebergQty:
            p['icebergQty'] = icebergQty

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._post('v3/order?', p)


    def queryOrder(self, symbol, orderId=None, origClientOrderId=None, recvWindow=None):
        """
        Check an order's status.
        GET /api/v3/order
        """
        
        p = {'symbol': symbol, 'timestamp': int((time.time() * 1000) - self.time_offset)}

        if orderId:
            p['orderId'] = orderId

        elif origClientOrderId:
            p['origClientOrderId'] = origClientOrderId

        else:
            raise MalformedRequest("Either orderId or origClientOrderId must be sent.")

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._get('v3/order?', p)


    def deleteOrder(self, symbol, orderId=None, origClientOrderId=None, newClientOrderId=None, recvWindow=None):
        """
        Cancel an active order.
        DELETE /api/v3/order
        """
        
        p = {'symbol': symbol, 'timestamp': int((time.time() * 1000) - self.time_offset)}

        if orderId:
            p['orderId'] = orderId

        if origClientOrderId:
            p['origClientOrderId'] = origClientOrderId

        if newClientOrderId:
            p['newClientOrderId'] = newClientOrderId

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._delete('v3/order?', p)


    def openOrders(self, symbol, recvWindow=None):
        """
        Get all open orders on a symbol.
        GET /api/v3/openOrders
        """
        
        p = {'symbol': symbol, 'timestamp': int((time.time() * 1000) - self.time_offset)}

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._get('v3/openOrders?', p)


    def allOrders(self, symbol, orderId=None, limit=500, recvWindow=None):
        """
        Get all account orders; active, canceled, or filled.
        GET /api/v3/allOrders
        """
        
        p = {'symbol': symbol, 'limit': limit, 'timestamp': int((time.time() * 1000) - self.time_offset)}

        if orderId:
            p['orderId'] = orderId

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._get('v3/allOrders?', p)


    def account(self, recvWindow=None):
        """
        Get current account information.
        GET /api/v3/account
        """
        
        p = {'timestamp': int((time.time() * 1000) - self.time_offset)}

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._get('v3/account?', p)


    def myTrades(self, symbol, limit=500, fromId=None, recvWindow=None):
        """
        Get trades for a specific account and symbol.
        GET /api/v3/myTrades
        https://www.binance.com/restapipub.html#account-trade-list-signed
        """
        
        p = {'symbol': symbol, 'limit': limit, 'timestamp': int((time.time() * 1000) - self.time_offset)}

        if fromId:
            p['fromId'] = fromId

        if recvWindow:
            p['recvWindow'] = recvWindow
        
        p['signature'] = self._sign(p)

        return self._get('v3/myTrades?', p)


    # User stream endpoints
    def new_stream(self):
        """
        Start a new user data stream.
        POST /api/v1/userDataStream
        https://www.binance.com/restapipub.html#start-user-data-stream-api-key
        """

        assert(self.key)

        res = self._post('v1/userDataStream')
        
        return res['listenKey']


    def keepalive_stream(self, listenKey):
        """
        PING a user data stream to prevent a time out.
        PUT /api/v1/userDataStream
        https://www.binance.com/restapipub.html#keepalive-user-data-stream-api-key
        """

        assert(self.key)

        param = "listenKey=%s" % (listenKey)

        return self._put('v1/userDataStream', param)


    def keepalive_stream(self, listenKey):
        """
        PING a user data stream to prevent a time out.
        DELETE /api/v1/userDataStream
        https://www.binance.com/restapipub.html#close-user-data-stream-api-key
        """

        assert(self.key)

        param = "listenKey=%s" % (listenKey)

        return self._delete('v1/userDataStream', param)
