
import pandas as pd
import requests
import json
import numpy as np
from binance.client import Client
from pyti.smoothed_moving_average import smoothed_moving_average as sma
from plotly.offline import plot
import plotly.graph_objs as go
import datetime
import time


#Mayer Multiple
#current price / 200 day moving average
#9500/8370= 1.13
#if over 2.0 then bitcoin is expensive
#between 2.0 and 1.2 then normal high
#between 1.2 and 1.0 is normal
#less than 1.0 cheap


client = Client(api_key='api_key',api_secret='api_secret')

 
def main():
    period = 100
    pair = "BTCUSDT"

    while True:
        print(pair)
        print(datetime.datetime.now())
        currentPrice = getCurrentPriceData(pair)
        SMA200Day = get200DaySMA(pair)

        print("Current Price: " + str(currentPrice))
        print("200 Day SMA: " + str(SMA200Day))
        print("Mayer Multiple: " + str(float(currentPrice)/float(SMA200Day)))

        if((float(currentPrice)/float(SMA200Day)) >= 2):
            print("Expensive")
        elif((float(currentPrice)/float(SMA200Day)) < 2 and (float(currentPrice)/float(SMA200Day)) >= 1.2):
            print("Normal High")
        elif((float(currentPrice)/float(SMA200Day)) < 1.2 and (float(currentPrice)/float(SMA200Day)) >= 1):
            print("Normal")
        else:
            print("Cheap")

        df = get200Day(pair)
        print(df)
        time.sleep(period)

 

#Get Current Pair Price

def getCurrentPriceData(pair):
    prices = client.get_all_tickers()
    df = pd.DataFrame(prices)
    df = df.loc[df['symbol']==pair]
    return df['price'].values[0]

 
#Get 200 Day Simple Moving Average

def get200DaySMA(pair):
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1DAY, "200 day ago UTC")
    df = pd.DataFrame(klines)
    df = df[[0,1,2,3,4,5]]
    df.columns = ['Open Time','Open','High','Low','Close','Volume']
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['Close'] = df['Close'].astype('float64')
    return df["Close"].mean()

 
#Get 200 Day DataFrame

def get200Day(pair):
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1DAY, "200 day ago UTC")
    df = pd.DataFrame(klines)
    df = df[[0,1,2,3,4,5]]
    df.columns = ['Open Time','Open','High','Low','Close','Volume']
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['Close'] = df['Close'].astype('float64')
    return df

if __name__ == "__main__":
    main()