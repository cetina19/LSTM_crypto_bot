from time import sleep
import urllib3
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
import pickle

from stable_baselines import ACKTR
from stable_baselines.common.evaluation import evaluate_policy

df = pd.read_csv('ETH_1min.csv')

env = gym.make('stocks-v0', df=df, frame_bound=(5,150), window_size=5)

model = ACKTR.load("bot2_1.zip")

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
    
    data = vbt.YFData.download(symbols= 'ETH-USD', period="150m", interval="5m")
    df = data.get()
    
    #print(df)

    env = gym.make('stocks-v0', df=df, frame_bound=(5,75), window_size=5)
    obs = env.reset()
    #print(obs.shape)
    #print(obs)
    #%store -r next_week_SOL
    #file = open('Next_Week_Predictions.pickle', 'rb')
    tomorrow_prediction = pickle.load(open('Next_Week_Predictions.pickle', 'rb'))
    tomorrow_prediction[0]*=0.71
    tomorrow_prediction[0]*=0.86
    change_quantity = tomorrow_prediction[0] + tomorrow_prediction[1]
    print(tomorrow_prediction)
    print(" *** ",change_quantity)
    current_eth = vbt.YFData.download(symbols= 'ETH-USD', period="1d")
    print("In tomorrow net money change int the account = ",current_eth * change_quantity)
    print("*****************************************")
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
manager.every().do(check_order_status)
manager.every().minutes.do(get_bars)
manager.start()