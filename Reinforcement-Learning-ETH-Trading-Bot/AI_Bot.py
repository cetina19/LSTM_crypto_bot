from time import sleep
import matplotlib
from numpy import append
import config
import vectorbt as vbt
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from alpaca_trade_api.rest import REST
import gym
import gym_anytrading

from stable_baselines import ACKTR
from stable_baselines.common.evaluation import evaluate_policy

df = pd.read_csv('dfs.csv')

env = gym.make('stocks-v0', df=df, frame_bound=(5,150), window_size=5)

model = ACKTR.load("bot.zip")

#mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=100)
obs = env.reset()

alpaca = REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets")

in_position_quantity = 0
pending_orders = {}
dolar_amount = 100000
logfile = 'trade.log'

def check_order_status():
    global in_position_quantity
    removed_order_ids = []
    print("{} - checking order status".format(datetime.now().isoformat()))

    if(len(pending_orders.keys()) > 0):
        print("Found the Pending the orders")

        for order_id in pending_orders:
            order = alpaca.get_order(order_id)

            if order.filled_at is not None:
                filled_message = "order to {} {} {} was filled {} at price {}\n".format(order.side, order.qty, order.symbol, order.filled_at, order.filled_avg_price)
                print(filled_message)
                with open(logfile, 'a') as f:
                    f.write(filled_message)
                
                if (order.side=='buy'):
                    in_position_quantity = float(order.qty)
                else:
                    in_position_quantity = 0

                removed_order_ids.append(order_id)
            else:
                print( "order is not filled")
    for order_id in removed_order_ids:
        del pending_orders[order_id]

def send_orders(symbol, quantity, side):
    print("{} - sending {} bars".format(datetime.now().isoformat(), side) )
    order = alpaca.submit_order(symbol, quantity, side, 'market', 'gtc')
    print(order, " *** Order is sent")
    pending_orders[order.id] = order

def get_bars():
    print("{} - getting bars".format(datetime.now().isoformat()))
    data = vbt.CCXTData.download(['ETH/USDT'], start='15 minutes ago', timeframe='1m')
    df = data.get()
    #df.index = pd.to_datetime(df.index).tz_localize(None)
    print(df)

    env = gym.make('stocks-v0', df=df, frame_bound=(5,75), window_size=5)
    obs = env.reset()
    print(obs.shape)
    print(obs)
    last_action = 0

    for _ in range(30):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        env.render()
        last_action = action
        if done : 
            break
    env.reset()
    env.close()

    if(last_action==1):
        print("Buy Order is sent")
    elif(last_action==0):
        print("Sell Order is sent")

manager = vbt.ScheduleManager()
manager.every().minute.do(check_order_status)
manager.every(15, 'minutes').do(get_bars)
#manager.every().minute.do(check_order_status)
#manager.every(15, 'minutes').do(get_bars)
manager.start()

#endpoint = "https://paper-api.alpaca.markets"