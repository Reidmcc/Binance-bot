# Binance-bot
#### Python bot for trading on the Binance cryptocurrency exchange.

There are two strategies, cross-pair arbitrage and breakout trend trading. 

#### Cross-pair arbitrage: 

##### Files: 
- mult_arbit.py
- price_monitor.py
- run_mult_arbit.py

##### Status:

The point is to turn altcoins into more altcoins. In optimal conditions it can cycle multiple times a minute. It only works in a very specific context:
- You have to be in a low-fee environment. Any fee above 0.1% kills it, it works on a 0.5% margin trigger over three trades.
- The altcoin you're going for has to trade against two base coins that also trade against each other.

So if you're doing XLM on Binance examples are:
- XLM->ETH->BTC->XLM
- XLM->BNB->ETH->XLM
   
**WARNING: This strategy is super risky. It works best when all three pairs are trading sideways or trending gently.
The bot knows nothing about market status other than current price ratios; rapid price swings can easily leave you mid-cycle
holding a bag you don't want.**
![rockfish icon long flip](https://user-images.githubusercontent.com/43561569/52517024-0c518c00-2bfa-11e9-9cd0-e2443d7868f1.png)
Like this strategy? Check out [Rockfish](https://github.com/Reidmcc/rockfish), which implements a similar strategy for the Stellar Decentralized Exchange.

### Breakout trend trading:

##### Files:
- turtle_trade.py
- run_turtle.py

##### Status:
This strategy looks for X period high/low breakouts and bets with the break direction. It's inspired by the turtle traders
who did commodities in the 1980s (http://www.tradingblox.com/originalturtles/). They were trading on 10-day breakouts, which 
is far too slow for cryptocurrency exchanges, so the bot is set to X hours, not days. Problem is that according to my testing
it barely breaks even (or goes negative) on all breakout ranges I've tested.

**WARNING: As this strategy currently stands it does not profit. If you want to try it _backtest it hard!_**

   
#### Both strategies need these files:
- api.py
- data_checks.py
- excepts.py
- log.py
      
     
_(Standard disclaimer saying this isn't investment advice and bots can lose your money real fast. No warranties, etc. etc.)_

#### Install instructions as requested in an issue:

There is no fancy install; you set up a local Python virtual environment as you would any other, drop the .py files into the directory, revise the parameter sections that refer to certain coins and the rules for them, and run the desired executor file (run_mult_arbit.py or run_turtle.py). You need to create an API key on your Binance account and add the key and secret where indicated near the top of the files as [API key] and [API secret]. The log text files will generate into the directory.

Binance's rules for trading pairs (min amount, etc.) are here: https://support.binance.com/hc/en-us/articles/115000594711-Trading-Rule

For my developer environment I use PyCharm: https://www.jetbrains.com/pycharm/. There are many other IDEs, or you can do it on the command line as explained at https://packaging.python.org/guides/installing-using-pip-and-virtualenv/.

If you're new to crypto trading I strongly recommend you acclimate with some manual trading; if you just run the bot without context knowledge you'll have a bad time.
