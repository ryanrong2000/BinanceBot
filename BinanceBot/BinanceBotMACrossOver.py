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

client = Client(api_key='api_key',api_secret='api_secret')

def main():
    period = 10
    pair = "BTCUSDT"
    buyPercentage = 0.03
    sellPercentage = 0.03
    stopLoss = 0.1 #10 percent

    while True:
        print(pair)
        print(datetime.datetime.now())
        currentPrice = getCurrentPriceData(pair)
        Hour1Avg = get1HourAvg(pair)
        Hour24Avg = get24HourAvg(pair)
        buyPrice = Hour1Avg - Hour1Avg * buyPercentage #3 percent lower then hour moving average
        sellPrice = Hour1Avg + Hour1Avg * sellPercentage #3 percent higher then hour moving average

        print("Current Price:" + str(currentPrice))
        print("1 Hour Average: " + str(Hour1Avg))
        print("24 Hour Average:" + str(Hour24Avg))
        print("Buy Price:" + str(buyPrice))
        print("Sell Price:" + str(sellPrice))

        if(float(currentPrice) <= float(buyPrice)):
            print("Buy")
        elif(float(currentPrice) >= float(sellPrice)):
            print("Sell")
        else:
            print("Do Nothing")
        #get recent trade data
        #tradesDataFrame = getMyTradeData()
        #print(tradesDataFrame)

        time.sleep(period)

def getCurrentPriceData(pair):
    prices = client.get_all_tickers()
    df = pd.DataFrame(prices)
    df = df.loc[df['symbol']==pair]
    return df['price'].values[0]

def get24HourAvg(pair):
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
    df = pd.DataFrame(klines)
    df = df[[0,1,2,3,4,5]]
    df.columns = ['Open Time','Open','High','Low','Close','Volume']
    #df['Open Time'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['Close'] = df['Close'].astype('float64')
    return df["Close"].mean()

def get1HourAvg(pair):
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
    df = pd.DataFrame(klines)
    df = df[[0,1,2,3,4,5]]
    df.columns = ['Open Time','Open','High','Low','Close','Volume']
    #df['Open Time'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['Close'] = df['Close'].astype('float64')
    return df["Close"].mean()

def getMyTradeData():
    trades = client.get_my_trades(symbol=pair)
    df = pd.DataFrame(trades)
    return df


if __name__ == "__main__":
    main()
