# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 20:35:24 2020

DOUBLE/TRIPLE CROSSOVER MA STRATEGY IMPLEMENTATION:
    DATA USED: 24 HOUR FOREX EUR-USD CURRENCY EXCHANGE - NOV 9 2020
    DATA TYPE: TOP OF ORDER BOOK BID/BUY TICKER
    OPENING PRICE: 1.8872
    CLOSING PRICE: 1.8352
        
ALGORITHM PROCESS:
    1. COMPUTE AVERAGE BETWEEN BUY/SELL
    2. COMPUTE 4 SECOND AVERAGE OF BUY/SELL-AVERAGE
    3. COMPUTE 1 MIN EMA OF 4 SECOND AVERAGE
    4. COMPUTE 3 MIN EMA OF 4 SECOND AVERAGE
    5. DETERMINE CROSSOVER POINTS AND MOVEMENT FOR BUY/SELL
    6. ESTIMATE PROFITS/LOSSES

MA PARAMETERS:
    TYPE: EXPONENTIAL MOVING AVERAGE
    1 MIN: 15 POINTS - ALPHA = .8
    3 MIN: 45 POINTS - ALPHA = .4
    5 MIN: 75 POINTS - ALPHA = .2
    
OUTPUT UPDATE/DECISION RATE:
    4 SECONDS
    
SIMULATION RESULTS:
    STARTING VALUES: 0 in capital, 0 shares
    ENDING VALUES:
        
@author: mecap
"""



#import serial
import csv
import time
import matplotlib.pyplot as plt
import numpy as np

data = np.genfromtxt("C:/Users/mecap/Desktop/600/EURUSD_Nov9_2020.csv", delimiter=",", names=["0", "1","2","3","4","5","6","7", "8", "9", "10"])

plot1 = plt.figure(1)
plt.plot(data['10'], data['8'], data['10'], data['3'], data['10'], data['4'])
#plt.axis([0,1000,1.188,1.190])
plt.title("Top Bid, Top Ask, Avg")


time = np.array(data['10'])
price = np.array(data['8'])

#1 min EMA and 3 min EMA for crossover method
#new output every 4 seconds

sec_cnt = 4
index_cnt = 0
avg_index_cnt = 0
summer = 0
avg_cnt = 0
avg_array = [0] * 21600
#go through and take 4 second averages of prices
while sec_cnt < 86400:
    if time[index_cnt] <= sec_cnt:
        summer = summer + price[index_cnt]
        index_cnt = index_cnt + 1
        avg_cnt = avg_cnt + 1
    elif time[index_cnt] > sec_cnt:
        if avg_cnt > 0:
            avg_array[avg_index_cnt] = summer / avg_cnt
        else:
            avg_array[avg_index_cnt] = avg_array[avg_index_cnt - 1]
        summer = 0
        avg_cnt = 0
        sec_cnt = sec_cnt + 4
        avg_index_cnt = avg_index_cnt + 1

avg_array[21599] = avg_array[21598]

#plot for verification
time_4sec = [0] * 21600
counter = 0
counter2 = 0
while counter2 < 21600:
    time_4sec[counter2] = counter
    counter = counter + 4
    counter2 = counter2 + 1

plot2 = plt.figure(2)    
plt.plot(time_4sec, avg_array)
plt.title("4 Second Time Average")

        
#go through and take 1 min EMA of 4 second averages
alpha = .8
ma_1min = [0] * 21600
ma_indexer = 14
numerator = 0
denominator = 0

while ma_indexer < 21600:
    numerator = avg_array[ma_indexer]
    for x in range(1,15):
        numerator = numerator + (1-alpha)**x * avg_array[ma_indexer - x]
    denominator = 1
    for x in range(1,15):
        denominator = denominator + (1-alpha)**x
    ma_1min[ma_indexer] = numerator / denominator
    ma_indexer = ma_indexer + 1

for x in range(14):
    ma_1min[x] = ma_1min[14]


#again for 3 min
alpha = .4
ma_3min = [0] * 21600
ma_indexer = 44

while ma_indexer < 21600:
    numerator = avg_array[ma_indexer]
    for x in range(1,45):
        numerator = numerator + (1-alpha)**x * avg_array[ma_indexer - x]
    denominator = 1
    for x in range(1,45):
        denominator = denominator + (1-alpha)**x
    ma_3min[ma_indexer] = numerator / denominator
    ma_indexer = ma_indexer + 1

for x in range(44):
    ma_3min[x] = ma_3min[44]



#Crossover Strategy
#if short term value crosses long term value from above, sell
#if short term value crosses long term value from below, buy
tracker = [0] * 21600
buyplot = [0] * 21600
sellplot =[0] * 21600
for x in range(44, 21600):
    if ma_1min[x] > ma_3min[x]:
        tracker[x] = 1
    else:
        tracker[x] = -1

for x in range(45, 21600):
    if tracker[x] != tracker[x-1]:
        if (tracker[x] == 1): #low to high -- buy
            buyplot[x] = ma_1min[x]
        else: #high to low -- sell
            sellplot[x] = ma_1min[x]

plt.figure(3)
plt.plot(time_4sec, avg_array, time_4sec, ma_1min, time_4sec, ma_3min)
plt.title("1 and 3 min moving average")
for x in range(45, 21600):
    if(buyplot[x] != 0):
        plt.plot(time_4sec[x], buyplot[x], color = 'red', marker=".", markersize=5)
    if (sellplot[x] != 0):
        plt.plot(time_4sec[x], sellplot[x], color = 'purple',marker=".", markersize=5)
plt.show() 

#simulate trading process
capital = 0
capital_plot = [0]*21600
shares = 0
sells_total = 0
buys_total = 0
for x in range(44, 21600):
    if(buyplot[x] != 0):
        capital = capital - buyplot[x]
        shares = shares + 1
        buys_total = buys_total + 1
    if(sellplot[x] != 0):
        capital = capital + sellplot[x]
        shares = shares - 1
        sells_total = sells_total + 1
    capital_plot[x] = capital

plt.figure(4)
plt.plot(time_4sec, capital_plot)
plt.title("Profit/Loss Plot")
plt.show()   
   
#Triple Crossover for Double Validation:    
   
#stuff for com port to FPGA
#during testing,
#create a ticker timer, if value in col H of message.csv is less than ticker timer
#then write col E value to UART

"""
seconds = 60;
time = numpy.array(data['7'])
stock_price = numpy.array(data['4'])

s = serial.Serial('COM7') #change com7 to actual com port

msg_cntr = 1;
init_time = time.perf_counter()

while msg_cntr < 155936:
    curr_time = time.perf_counter() - init_time
    if curr_time > msg_Hcol;

s = serial.Serial('COM7') #change com7 to actual com port
s.write(b'')
"""

