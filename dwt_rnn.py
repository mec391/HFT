# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 23:33:19 2020


DWT + RNN


PREPROCESSING:
    GROUP TICKS BY THE MINUTE
    TAKE 1 MIN AVG
    TAKE PSEUDOLOG RETURN USING CURRENT AND PREV 1 MIN AVG
    TAKE ALL DATA WITHIN 1 MINUTE(BEFORE AVGING) AND THROW INTO DWT
    ITERATE DWT UNTIL THERE IS 1 WAVELET COEFFEICNT AND 1 SCALING COEFFICENT
    GO BACK 1 ITERATE LEVEL AND THOSE COEFFIENTS WILL EITHER BE 3 OR 2, IF 2, PAD WITH 0
    FINAL VECTOR [W1 W2a W2b (W2c OR 0) V1 V2a V2b (V2c  OR 0)]
    
    INPUT TO NN: (FINAL VECTOR, PSEDUOLOG RETURN) OF T, T-1, T-2
    TOTAL INPUTS: 27
    OUTPUT OF NN:  PREDICTED PSEUDOLOG RETURN T+1 USED TO SOLVE FOR PREDICTED AVG PRICE T+1
    TOTAL OUTPUTS:1
    NN ARCHITECTURE: 
    5 hidden layers - 27 22 17 11 6 1 neurons, tahn AF in cells, LINEAR IN OUTPUT
    GATED RECURRENT UNIT NEURAL NETWORK

Total trainable parameters  11,100 
Total training time  100.55 s (200 epochs)
Total time per prediction  57.75 µs
    TRAINING: MEAN SQUARE ERROR LOSS FN, ADAM
    
    !!!IDEA: USE VERY SHORT TERM EMA TO COMPENSATE FOR ISSUES WITH DWT+RNN
    
    
@author: mecap
"""

#import serial
import math
#import pywt
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
#3= sellprice
#4= buyprice
#5= sellvol
#6= buyvol

"""
data = np.genfromtxt("C:/Users/mecap/Desktop/600/EURUSD_Nov9_2020.csv", delimiter=",", names=["0", "1","2","3","4","5","6","7", "8", "9", "10"])
plot1 = plt.figure(1)
plt.plot(data['10'], data['8'], data['10'], data['3'], data['10'], data['4'])
#plt.axis([0,1000,1.188,1.190])
plt.title("Top Bid, Top Ask, Avg")

time = np.array(data['10'])
price = np.array(data['8'])
"""
###tick data instead of LOB data inserted here:
data = np.genfromtxt("C:/Users/mecap/Desktop/600/lobster_apple.csv", delimiter=",", names=["0", "1","2","3","4","5","6","7"])
time = np.array(data['6'])
price = np.array(data['7'])

#need to go through and update parameters to make new data file

plt.figure(1)
plt.plot(time, price)

minn = 60
summs= 0
cnt =0
minavg = [0] * 390 #this may need adjusted
minavgcnt = 0
#take 1 min average
for x in range(0, 118497):
    if(time[x] < minn):
        summs = summs + price[x]
        cnt = cnt + 1
    else:
        if(cnt > 0):
            minavg[minavgcnt] = summs / cnt
        else:
            minavg[minavgcnt] = minavg[minavgcnt - 1] #in reality, if there is no data for the last minute, do not trade!! i think
        summs = 0
        cnt = 0
        minavgcnt = minavgcnt + 1
        minn = minn + 60
minavg[389] = minavg[388]
minplot = [0]*390
minplot[0] = 60
for x in range(1, 390):
    minplot[x] = minplot[x-1] + 60       

#plot2 = plt.figure(2)
plt.plot(minplot, minavg)
plt.title("1 minute average")


pseudo_returns = [0]*390
#take pseudolog returns
for x in range(1, 390):
    pseudo_returns[x] = np.log(minavg[x] / minavg[x-1]) * 100

plot2 = plt.figure(2)
plt.plot(minplot, pseudo_returns)
plt.title("pesudo returns")

#compute dwt -- 
def haarFWT ( signal, level ):

    s = .7071068;                  # scaling -- try 1 or ( .5 ** .5 )

    h = [ 1,  1 ];           # lowpass filter
    g = [ 1, -1 ];           # highpass filter        
    f = len ( h );           # length of the filter

    t = signal;              # 'workspace' array
    l = len ( t );           # length of the current signal
    y = [0] * l;             # initialise output

    t = t + [ 0, 0 ];        # padding for the workspace

    for i in range ( level ):

        y [ 0:l ] = [0] * l; # initialise the next level 
        l2 = l // 2;         # half approximation, half detail

        for j in range ( l2 ):            
            for k in range ( f ):                
                y [j]    += t [ 2*j + k ] * h [ k ] * s;
                y [j+l2] += t [ 2*j + k ] * g [ k ] * s;

        l = l2;              # continue with the approximation
        t [ 0:l ] = y [ 0:l ] ;

    return y

cnt = 0
mindwt = [0]*2000
minn = 60
output_indexer = 0
dwt_output = np.zeros((390,8))  #output depth --> 0-3: W3,2,2,2 ,,,4-7: V3,2,2,2
for q in range(0, 118496):
    if(time[q] < minn):
        mindwt[cnt] =  price[q]
        cnt = cnt + 1
    elif (cnt > 3):
        dwt_input = [0]*cnt
        sizer = cnt
        lengther = math.floor(math.log2(sizer))
        rounder = (math.log2(sizer))
#take size of input array, take log2
#take that value and round down, use for input level of dwt
#if log2 value is <.5 apply padding
        dwt_input = mindwt[0:cnt]
        haar_output2 = haarFWT(dwt_input, lengther-1)
        haar_output3 = haarFWT(dwt_input, lengther)
        if(int(rounder) + 1 - rounder > .5): #log2 is <.5, need to pad
            dwt_output[output_indexer,0] =  haar_output3[1]
            dwt_output[output_indexer,1:3] = haar_output2[2:4]
            dwt_output[output_indexer,3] = 0
            dwt_output[output_indexer,4] = haar_output3[0]
            dwt_output[output_indexer,5:7] = haar_output2[0:2]
            dwt_output[output_indexer,7] = 0
        else: #log2 is <.5, no need to pad
            dwt_output[output_indexer,0] = haar_output3[1]
            dwt_output[output_indexer,1:4] = haar_output2[3:6]
            dwt_output[output_indexer,4] = haar_output3[0]
            dwt_output[output_indexer,5:8] = haar_output2[0:3]
        cnt=0
        minn = minn + 60
        output_indexer = output_indexer + 1
    else: #if no data or only 1-3 data value, carry value of prev minute
        dwt_output[output_indexer][:] = dwt_output[output_indexer-1][:]
        cnt=0
        minn=minn + 60
        output_indexer = output_indexer + 1

dwt_output[389,:] = dwt_output[388,:]


combiner = np.zeros(390)
combiner = dwt_output[:,0] * dwt_output[:,4]
plot3 = plt.figure(3)
#plt.plot(minplot, dwt_output[:,0], 'red',minplot, dwt_output[:,4],'blue', minplot, minavg,'green', minplot, combiner, 'orange')
plt.plot(minplot, dwt_output[:,0], 'red',minplot, dwt_output[:,4],'blue', minplot, minavg,'green')#, minplot, combiner, 'orange')
plt.title("top wavelet coef, top scale coef, 1 min avg")
plt.show()


