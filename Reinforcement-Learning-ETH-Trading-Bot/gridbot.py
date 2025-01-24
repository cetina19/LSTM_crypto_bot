from distutils.command.config import config
import ccxt, gridBot_config, time, sys

exchange = ccxt.ftxus({
    'apikey': gridBot_config.API_KEY,
    'secret': gridBot_config.SECRET_KEY
})

ticker = exchange.fetch_ticker(gridBot_config.SYMBOL)

buy_orders = []
sell_orders = []

#initial_buy_order = exchange.create_market_buy_order(gridBot_config.SYMBOL, gridBot_config.POITION_SIZE * gridBot_config.NUM_SELL_GRID_SIZE)

for i in range(gridBot_config.NUM_BUY_GRID_SIZE):
    price = ticker['bid'] - (gridBot_config.GRID_SIZE * (i+1))
    print("Selling market order {}".format(price))
    order = exchange.create_limit_buy_order(gridBot_config.SYMBOL, gridBot_config.POITION_SIZE, price)