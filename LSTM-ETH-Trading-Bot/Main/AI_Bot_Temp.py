from distutils.util import change_root
from lib2to3.pygram import Symbols
from time import sleep
from turtle import pos
import numpy as np
import urllib3
import matplotlib
from numpy import append
import config
import vectorbt as vbt
import pandas as pd
import pandas_ta as ta
from datetime import datetime as dt
from alpaca_trade_api.rest import REST
import gym
import gym_anytrading
import pickle
import yfinance as yf

from stable_baselines import ACKTR
from stable_baselines.common.evaluation import evaluate_policy

df = pd.read_csv('ETH_1min.csv')

print("You started with 5.3 Ethereum")


env = gym.make('stocks-v0', df=df, frame_bound=(5,150), window_size=5)

model = ACKTR.load("bot.zip")

obs = env.reset()

alpaca = REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets")

in_position_quantity = 0
pending_orders = {}
dolar_amount = 100000
logfile = 'trade.log'

def check_order_status():
    global in_position_quantity
    removed_order_ids = []
    print("{} - checking order status".format(dt.now().isoformat()))

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
    print("{} - sending {} bars".format(dt.now().isoformat(), side) )
    order = alpaca.submit_order(symbol, quantity, side, 'market', 'gtc')
    print(order, " *** Order is sent")
    pending_orders[order.id] = order

def get_bars():
    print("{} - getting bars".format(dt.now().isoformat()))
    end = dt.now()
    start = pd.Timedelta(days=7)
    data = yf.download(Symbols='ETH-USD',tickers='ETH-USD',start=end-start,end=end)

    tomorrow_prediction = pickle.load(open('Next_Week_Predictions.pickle', 'rb'))
    tomorrow_prediction[0]*=(0.488*0.71/(0.71+0.86))
    tomorrow_prediction[1]*=(0.369*0.86/(0.71+0.86))
    buy_sel_signal = np.array([])
    change_quantity = np.array([])
    latest_value = data['Close'][-1]
    for i in range(len(tomorrow_prediction[0])):
        if(tomorrow_prediction[0][i] * tomorrow_prediction[1][0] > 0):
            if(tomorrow_prediction[0][i] < 0):
                buy_sel_signal = np.append(buy_sel_signal, -1)
            else:
                buy_sel_signal = np.append(buy_sel_signal, 1)
        else:
            buy_sel_signal = np.append(buy_sel_signal,0)
    
    position = []
    for i in range(len(buy_sel_signal)):
        if buy_sel_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
    
    for i in range(len(buy_sel_signal)):
        if buy_sel_signal[i] == 1:
            position[i] = 1
        elif buy_sel_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
    
    print(buy_sel_signal," *** ",position)
        #change_quantity = np.append(change_quantity, (tomorrow_prediction[0][i] + tomorrow_prediction[1][i]) )
        #latest_value = latest_value + latest_value*change_quantity[i]
    change_quantity = tomorrow_prediction[0] + tomorrow_prediction[1]
    #change_quantity = change_quantity[1:]
    #print(change_quantity)
    total_eth = 5.3
    print("***",(tomorrow_prediction[0][0] + tomorrow_prediction[1][0]) / 2,"***")
    latest_eth = vbt.YFData.download(symbols= 'ETH-USD', period="1d").get('Close')
    current_gas =  latest_eth * vbt.YFData.download(symbols= 'GAS-ETH', period="1d").get('Close')
    #latest_eth =current_eth_frame.data['ETH-USD'].Close
    #print(current_gas)
    one_hundred_dollar = (100+current_gas[0]) / latest_eth[0]
    #print(one_hundred_dollar)
    #print(latest_eth[0]," &&& 100 Dollar ethereum worth gas = ",one_hundred_dollar)
    print("*****************************************")
    print("*****************************************\n")
    print("Values are calculated for 1 Ethereum (",latest_eth[0]," dollar)\n")
    for i in range(7):
        if((tomorrow_prediction[0][i] + tomorrow_prediction[1][i]) / 2 <= -0.05):
            print("After ",i+1," day net money change in the account = ", one_hundred_dollar , " ethereum sell.")
            total_eth-=one_hundred_dollar
        elif((tomorrow_prediction[0][i] + tomorrow_prediction[1][i]) / 2 >= 0.05):
            total_eth+=one_hundred_dollar
            print("After ",i+1," day net money change in the account = ", one_hundred_dollar , " ethereum buy.")
        else:
            print("After ",i+1," day no net money change in the account if you hold.")
    print("\n*****************************************")
    print("*****************************************")
    print("\nTotal Ethereum in the account = ", total_eth)
    '''last_action = 0

    if(last_action==1):
        print("Buy Order is sent")
    elif(last_action==0):
        print("Sell Order is sent")'''

#total_eth = 5.3
manager = vbt.ScheduleManager()
manager.every().do(check_order_status)
manager.every(5).seconds.do(get_bars)
manager.start()