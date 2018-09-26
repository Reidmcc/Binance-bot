# Binance-bot
Python bot for trading on the Binance cryptocurrency exchange.

There are two strategies, cross-pair arbitrage and breakout trend trading. 

Cross-pair arbitrage:
  Files: 
    mult_arbit.py
    price_monitor.py
    run_mult_arbit.py
  Status:
    The point is to turn altcoins into more altcoins. In optimal conditions a cycle can execute in seconds and be ready to go again.
    It only works in a very specific context:
      You have to be in a low-fee environment. Any fee above 0.1% kills it, it works on a 0.5% margin trigger over three trades.
      The altcoin you're going for has to trade against two base coins that also trade against each other.
    So if you're doing XLM on Binance examples are:
      XLM->ETH->BTC->XLM
      XLM->BNB->ETH->XLM
   
  WARNING: 
    This strategy is super risky. It works best when all three pairs are trading sideways or trending gently.
    The bot knows nothing about market status other than current price ratios; rapid price swings can easily leave you mid-cycle
    holding a bag you don't want. 
   
   
Breakout trend trading:
  Files:
    turtle_trade.py
    run_turtle.py
  Status:
    This strategy looks for X period high/low breakouts and bets with the break direction. It's inspired by the turtle traders
    who did commodities in the 1980s (http://www.tradingblox.com/originalturtles/). They were trading on 10-day breakouts, which 
    is far too slow for cryptocurrency exchanges, so the bot is set to X hours, not days. Problem is that according to my testing
    it barely breaks even (or goes negative) on all breakout ranges I've tested.

  WARNING:
    As this strategy currently stands it does not profit. If you want to try it backtest it hard.

   
Both strategies need these files:
  api.py
  data_checks.py
  excepts.py
  log.py
      
     
(Standard disclaimer saying this isn't investment advice and bots can lose your money real fast. No warranties, etc. etc.)
