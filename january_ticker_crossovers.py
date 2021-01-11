# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 17:53:40 2021

@author: mecap



Script that uses tick data to compute EMAs, as opposed to top of book data
"""
import serial
import datetime
import time
import struct
import matplotlib.pyplot as plt
import numpy as np
import math



data = np.genfromtxt("C:/Users/mecap/Desktop/600/lobster_apple.csv", delimiter=",", names=["0", "1","2","3","4","5","6","7"])
ticker_time = np.array(data['6'])
ticker_price = np.array(data['7'])

plt.figure(1)
plt.plot(ticker_time, ticker_price)



##### BEGIN AVG DATA, change 'avg_value' variable to change the avg timeframe
avg_value = 4
sec_cnt = avg_value
index_cnt = 0
avg_index_cnt = 0
summer = 0
avg_cnt = 0
avg_array = [0] * int((math.floor(ticker_time[-1])) / avg_value)

#go through and take 4 second averages of prices
while sec_cnt < ticker_time[-1]:
    if ticker_time[index_cnt] <= sec_cnt:
        summer = summer + ticker_price[index_cnt]
        index_cnt = index_cnt + 1
        avg_cnt = avg_cnt + 1
    elif ticker_time[index_cnt] > sec_cnt:
        if avg_cnt > 0:
            avg_array[avg_index_cnt] = summer / avg_cnt
        else:
            avg_array[avg_index_cnt] = avg_array[avg_index_cnt - 1]
        summer = 0
        avg_cnt = 0
        sec_cnt = sec_cnt + avg_value
        avg_index_cnt = avg_index_cnt + 1

time_4sec = [0] * len(avg_array)
counter = avg_value
counter2 = 0
while counter2 < len(avg_array):
    time_4sec[counter2] = counter
    counter = counter + avg_value
    counter2 = counter2 + 1
  
plt.plot(time_4sec, avg_array)
plt.title("Ticker Plot in Price Vs Seconds, 4 Second Averages")
   
######END AVERAGE DATA




######BEGIN SHORT EMA- changs pts to change time length (based on avging time)
pts = 15
alpha = .8
ma_1min = [0] * len(avg_array)
ma_indexer = pts-1
numerator = 0
denominator = 0

while ma_indexer < len(avg_array):
    numerator = avg_array[ma_indexer]
    for x in range(1,pts):
        numerator = numerator + (1-alpha)**x * avg_array[ma_indexer - x]
    denominator = 1
    for x in range(1,pts):
        denominator = denominator + (1-alpha)**x
    ma_1min[ma_indexer] = numerator / denominator
    ma_indexer = ma_indexer + 1

for x in range(pts-1):
    ma_1min[x] = ma_1min[pts-1]


######END SHORT EMA


#####BEGIN LONG EMA
pts = 45
alpha = .4
ma_3min = [0] * len(avg_array)
ma_indexer = pts-1

while ma_indexer < len(avg_array):
    numerator = avg_array[ma_indexer]
    for x in range(1,pts):
        numerator = numerator + (1-alpha)**x * avg_array[ma_indexer - x]
    denominator = 1
    for x in range(1,pts):
        denominator = denominator + (1-alpha)**x
    ma_3min[ma_indexer] = numerator / denominator
    ma_indexer = ma_indexer + 1

for x in range(pts-1):
    ma_3min[x] = ma_3min[pts-1]
######END LONG EMA






####BEGIN TRADING STRATEGY
#if short term value crosses long term value from above, sell
#if short term value crosses long term value from below, buy
tracker = [0] * len(avg_array)
buyplot = [0] * len(avg_array)
sellplot =[0] * len(avg_array)
for x in range(pts-1, len(avg_array)):
    if ma_1min[x] > ma_3min[x]:
        tracker[x] = 1
    else:
        tracker[x] = -1

for x in range(pts, len(avg_array)):
    if tracker[x] != tracker[x-1]:
        if (tracker[x] == 1): #low to high -- buy
            buyplot[x] = ma_1min[x]
        else: #high to low -- sell
            sellplot[x] = ma_1min[x]

plt.figure(2)
plt.plot(time_4sec, avg_array)
plt.plot(time_4sec, ma_1min, time_4sec, ma_3min)
plt.title("dual moving averages crossover plot")
for x in range(45, len(avg_array)):
    if(buyplot[x] != 0):
        plt.plot(time_4sec[x], buyplot[x], color = 'red', marker=".", markersize=5)
    if (sellplot[x] != 0):
        plt.plot(time_4sec[x], sellplot[x], color = 'purple',marker=".", markersize=5)

#simulate trading process
capital =  0#-1 * ticker_price[0]
shares =  0#1
capital_plot = [0]*len(avg_array)
sells_total = 0
buys_total = 1
q = 0
for x in range(pts-2):
    capital_plot[x] = capital
    
for x in range(pts-1, len(avg_array)):
    if(buyplot[x] != 0):
        while ticker_time[q] <= time_4sec[x]:
                q = q + 1        
        capital = capital - ticker_price[q]
        shares = shares + 1
        buys_total = buys_total + 1
    if(sellplot[x] != 0):
        while ticker_time[q] <= time_4sec[x]:
                q = q + 1  
        capital = capital + ticker_price[q]
        shares = shares - 1
        sells_total = sells_total + 1
    capital_plot[x] = capital


plt.figure(3)
plt.plot(time_4sec, capital_plot)
plt.title("Profit/Loss Plot")
plt.show()   
####END TRADING STRATEGY