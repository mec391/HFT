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
import pywt
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
#3= sellprice
#4= buyprice
#5= sellvol
#6= buyvol
data = np.genfromtxt("C:/Users/mecap/Desktop/600/EURUSD_Nov9_2020.csv", delimiter=",", names=["0", "1","2","3","4","5","6","7", "8", "9", "10"])
plot1 = plt.figure(1)
plt.plot(data['10'], data['8'], data['10'], data['3'], data['10'], data['4'])
#plt.axis([0,1000,1.188,1.190])
plt.title("Top Bid, Top Ask, Avg")

time = np.array(data['10'])
price = np.array(data['8'])

minn = 60
summs= 0
cnt =0
minavg = [0] * 1440 #this may need adjusted
minavgcnt = 0
#take 1 min average
for x in range(0, 196573):
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
minavg[1439] = minavg[1438]
minplot = [0]*1440
minplot[0] = 60
for x in range(1, 1440):
    minplot[x] = minplot[x-1] + 60       

#plot2 = plt.figure(2)
plt.plot(minplot, minavg)
plt.title("1 minute average")


pseudo_returns = [0]*1440
#take pseudolog returns
for x in range(1, 1440):
    pseudo_returns[x] = np.log(minavg[x] / minavg[x-1]) * 100

plt.figure(2)
plt.plot(minplot, pseudo_returns)
plt.show()

#compute dwt -- download dwt package and make sure you get same answer given input
def haarFWT ( signal, level ):

    s = .5;                  # scaling -- try 1 or ( .5 ** .5 )

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


s0 = [ 56, 40, 8, 24, 48, 48, 40, 16 ];

print( "level 0" );
print( s0 );

print( "level 1" );
print( haarFWT (s0, 1 ) );

print( "level 2" );
print( haarFWT (s0, 2 ) );

print( "level 3" );
print( haarFWT (s0, 3 ) );

#first 6 values of level 3 is what we want