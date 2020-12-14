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
    period = 1000
    pair = "BTCUSDT"
    buyRangePercent = 1.005 #half percent
    sellRangePercent = 0.995 #half percent
    stopLossPercent = 0.9 #10 percent
    usdtMin = 500 #minimal amount to trigger trade
    btcMin = 0.05 #minimal amount to trigger trade

    while True:
        print(pair)
        print(datetime.datetime.now())
        currentPrice = getCurrentPriceData(pair)
        hour24High = get24HourHigh(pair)
        hour24Low = get24HourLow(pair)
        targetBuyPrice = buyRangePercent * hour24Low
        targetSellPrice = hour24High * sellRangePercent
        #usdtBalance = getUSDTBalance()
        usdtBalance = 1000
        #btcBalance = getBTCBalance()
        btcBalance = 0.1
        #lastOrderId = getLastOrderId(pair)
        #lastOrderSide = getOrderSide(pair, int(lastOrderId))
        lastOrderSide = "SELL"
        #lastOrderStatus = getOrderStatus(pair, int(lastOrderId))
        lastOrderStatus = "FILLED"
        #lastOrderAveragePrice = getTradeAveragePrice(pair, int(lastOrderId))
        takerFee = 0.01

        #Stop Loss Logic

        stopLossPrice = 0
        if(lastOrderSide =="BUY" and lastOrderStatus == "FILLED"):
            stopLossPrice = lastOrderAveragePrice * stopLossPercent

        print("USDT Amount: " + str(usdtBalance))
        print("BTC Amount: " + str(btcBalance))
        print("BTC Weight In USDT: " + str(float(btcBalance)*float(currentPrice)))
        #print("Last OrderId: " + str(int(lastOrderId)))
        print("Last Order Side: " + lastOrderSide)
        print("Last Order Status: " + lastOrderStatus)
        #print("Last Order Average Pirce: " + str(lastOrderAveragePrice))
        print("Current Price: " + str(currentPrice))
        print("24 Hour High: " + str(hour24High))
        print("24 Hour Low: " + str(hour24Low))
        print("Target Buy Price: " + str(targetBuyPrice))
        print("Target Sell Price: " + str(targetSellPrice))
        print("Stop Loss Price: " + str(stopLossPrice))
        print("Taker Fee: " + str(float(takerFee)))

       

        #Trade Logic
        if(lastOrderSide=="SELL" and lastOrderStatus=="FILLED" and float(usdtBalance) >= float(usdtMin) and float(currentPrice) <= float(targetBuyPrice)):
            print("Buy:" + str((float(usdtBalance)/float(currentPrice)) - float(takerFee)))
        elif(lastOrderSide=="BUY" and lastOrderStatus=="FILLED" and float(btcBalance) >= float(btcMin) and float(currentPrice) <= float(stopLossPrice)):
            print("SELL STOP LOSS QTY: " + str(float(btcBalance) - float(takerFee)))
        elif(lastOrderSide=="BUY" and lastOrderStatus=="FILLED" and float(btcBalance) >= float(btcMin) and float(currentPrice) >= float(targetSellPrice)):
            print("SELL: " + str(float(btcBalance) - float(takerFee)))
        else:
            print("Do Nothing")

        time.sleep(period)

 
#USDT Balance
def getUSDTBalance():
    info = client.get_account()
    df = pd.DataFrame(info['balances'])
    df = df.loc[df['asset']=='USDT']
    return df['free'].values[0]


#BTC Balance
def getBTCBalance():
    info = client.get_account()
    df = pd.DataFrame(info['balances'])
    df = df.loc[df['asset']=='BTC']
    return df['free'].values[0]


#Get Current Pair Price
def getCurrentPriceData(pair):
    prices = client.get_all_tickers()
    df = pd.DataFrame(prices)
    df = df.loc[df['symbol']==pair]
    return df['price'].values[0]


#Get Last OrderId
def getLastOrderId(pair):
    orders = client.get_all_orders(symbol=pair)
    df = pd.DataFrame(orders)
    df['orderId'] = df['orderId'].astype(float)
    return df['orderId'].max()

#Get Order Status
def getOrderStatus(pair, orderId):
    order = client.get_order(symbol=pair, orderId=orderId)
    return order['status']

 
#Get Order Side BUY OR SELL
def getOrderSide(pair, orderId):
    order = client.get_order(symbol=pair, orderId=orderId)
    return order['side']

 
#Get Average Trade Price
def getTradeAveragePrice(pair, orderId):
    trades = client.get_my_trades(symbol=pair)
    df = pd.DataFrame(trades)
    df['price'] = df['price'].astype(float)
    df = df.loc[df['orderId']==orderId]
    return df["price"].mean()

#Get 24 Hour High
def get24HourHigh(pair):
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
    df = pd.DataFrame(klines)
    df = df[[0,1,2,3,4,5]]
    df.columns = ['Open Time','Open','High','Low','Close','Volume']
    #df['Open Time'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['High'] = df['High'].astype('float64')
    return df["High"].max()

 
#Get 24 Hour Low
def get24HourLow(pair):
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
    df = pd.DataFrame(klines)
    df = df[[0,1,2,3,4,5]]
    df.columns = ['Open Time','Open','High','Low','Close','Volume']
    #df['Open Time'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['Low'] = df['Low'].astype('float64')
    return df["Low"].min()

   
#Get Taker Fee
def getTakerFee(pair):
    fees = client.get_trade_fee(symbol=pair)
    df = pd.DataFrame(fees["tradeFee"])
    return df["taker"]

#Market Buy
def buyMarket(pair, quantity):
    order = client.order_market_buy(symbol=pair,quantity=quantity)
    return order

#Market Sell
def sellMarket(pair, quantity):   
    order = client.order_market_sell(symbol=pair,quantity=quantity)
    return order


if __name__ == "__main__":
    main()
