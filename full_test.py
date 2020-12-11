# -*- coding: utf-8 -*-
"""
to do list:
    modify MA script so that it buys/sells at specified volume
    tweak sampling rates, moving average rates
    add third moving average
    create bid-ask volume spread as another indicator
    
    tie the uart rx and tx together with wires and receive the data back
    finish the uart tx code, loopback the data in the fpga back to python

UART TIMING LOOPBACK TEST WITH FPGA
bid and ask price: 0000.0000d -> 4 bytes 
bid and ask volume: 0000.0000d -> 4 bytes
must approximate value to right of decimal to fraction out of 16 

FOREX EUR-USD = ADDR 0 

byte structure(START, ADDR, BUYPRICE MSB3, 2, 1, 0, SELLPRICE MSB3, 2, 1, 0, BUYVOL MSB3, 2, 1, 0
               , SELLVOL MSB3, 2, 1, 0, STOP)

START = 8'b 11110000
STOP = 8'd' 00001111

total bytes per TX to FPGA: 19

@author: mecap
"""

import serial
import datetime
import time
import struct
import matplotlib.pyplot as plt
import numpy as np
#3= sellprice
#4= buyprice
#5= sellvol
#6= buyvol
data = np.genfromtxt("C:/Users/mecap/Desktop/600/EURUSD_Nov9_2020.csv", delimiter=",", names=["0", "1","2","3","4","5","6","7", "8", "9", "10"])
ticker_time = np.array(data['10'])
avg_price = np.array(data['8'])
input_sellprice = np.array(data['3'])
input_buyprice = np.array(data['4'])
input_sellvol = np.array(data['5'])
input_buyvol = np.array(data['6'])

ser = serial.Serial(port='COM3',baudrate=115200,timeout=(1)) #left usb port on laptop 


def send_data(sp_in, bp_in, sv_in, bv_in):
    start = int(240)
    stop = int(15)
    addr = int(0)

    sample_buyprice = bp_in
    buyprice_left = int(sample_buyprice)
    buyprice_right= float(str(sample_buyprice-int(sample_buyprice))[1:])
    #print(buyprice_right)
    ratio = (1/65536)
    buyprice_right = int((buyprice_right + ratio/2) // ratio * ratio * 65536)
    #print(buyprice_right)
    sample_sellprice = sp_in
    sellprice_left = int(sample_sellprice)
    sellprice_right= float(str(sample_sellprice-int(sample_sellprice))[1:])
    sellprice_right = int((sellprice_right + ratio/2) // ratio * ratio * 65536)

    sample_buysize = bv_in
    buysize_left = int(sample_buysize)
    buysize_right= float(str(sample_buysize-int(sample_buysize))[1:])
    buysize_right = int((buysize_right + ratio/2) // ratio * ratio * 65536)

    sample_sellsize = sv_in
    sellsize_left = int(sample_sellsize)
    sellsize_right= float(str(sample_sellsize-int(sample_sellsize))[1:])
    sellsize_right = int((sellsize_right + ratio/2) // ratio * ratio * 65535)


    start = struct.pack('!B',start)
    addr = struct.pack('!B',addr)
    buyprice_left = struct.pack('H', buyprice_left)
    buyprice_right =  struct.pack('H', buyprice_right)
    sellprice_left =  struct.pack('H', sellprice_left)
    sellprice_right =  struct.pack('H', sellprice_right)
    buysize_left =  struct.pack('H', buysize_left)
    buysize_right =  struct.pack('H', buysize_right)
    sellsize_left =  struct.pack('H', sellsize_left)
    sellsize_right =  struct.pack('H', sellsize_right)
    stop = struct.pack('!B',stop)



       
    ser.flushInput()
    ser.flushOutput() 
    
    ser.write(start)
    ser.write(addr)
    ser.write(buyprice_left)
    ser.write(buyprice_right)
    ser.write(sellprice_left)
    ser.write(sellprice_right)
    ser.write(buysize_left)
    ser.write(buysize_right)
    ser.write(sellsize_left)
    ser.write(sellsize_right)
    ser.write(stop)
    

#plt.style.use('ggplot')

def live_plotter(x_vec,y1_data,line1,inputter,identifier='',pause_time=0.0000001):
    if line1==[]:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13,6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        if(inputter == 'avg price'):
            line1, = ax.plot(x_vec,y1_data,'-o', color = 'blue')
        elif(inputter == 'sell'):
            line1, = ax.plot(x_vec[-1],y1_data[-1],marker='.',markersize=5, color = 'red')
        elif(inputter == 'buy'):
            line1, = ax.plot(x_vec[-1],y1_data[-1],marker='.',markersize=5, color = 'green')
        #update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()
    
    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    line1.set_xdata(x_vec)
    # adjust limits if new data goes beyond bounds
    #if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
    plt.ylim([np.min(y1_data)-(.0001),np.max(y1_data)+(.0001)])
        
    if np.min(x_vec)<=line1.axes.get_xlim()[0] or np.max(x_vec)>=line1.axes.get_xlim()[1]:
        plt.xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])    
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    # return line so we can update it again in the next iteration
    return line1

# MAIN FUNCTION ######################################
init_time = time.perf_counter()
init_avg_price = (input_sellprice[0] + input_buyprice[0])/2
row_counter = 0
line1 = []
yvec = np.array([init_avg_price]*1000)
xvec = np.array([0]*1000)
net_shares = 0
net_profit = 0
while True:
    current_time = time.perf_counter() - init_time
    if(current_time > ticker_time[row_counter]):
        send_data(input_sellprice[row_counter], input_buyprice[row_counter],
                  input_sellvol[row_counter], input_buyvol[row_counter])
        price_avgd = (input_sellprice[row_counter] + input_buyprice[row_counter])/2
        #updated plot price:
        yvec[-1] = price_avgd
        xvec[-1] = ticker_time[row_counter]
        line1 = live_plotter(xvec, yvec, line1, 'avg price')
        yvec = np.append(yvec[1:],0.0)
        xvec = np.append(xvec[1:],0.0)
        row_counter = row_counter + 1
    else:
        if(ser.in_waiting > 0):
            datas = [0]*19
            numbytes = ser.in_waiting
            #datas = struct.unpack('>19B', ser.read(19))
            z = '>'; zz = 'B'
            numbyte_string = z + str(numbytes) + zz
            datas = struct.unpack(numbyte_string, ser.read(numbytes))
            #plot the buy/sell
            #buysell byte => 1 buy, 2 sell
            if(datas[3] == 1):
                net_shares = net_shares + input_sellvol[row_counter-1]
                net_profit = net_profit - input_sellvol[row_counter-1]*input_sellprice[row_counter-1]
                yvec[-1] = price_avgd+1
                xvec[-1] = ticker_time[row_counter-1]
                line1 = live_plotter(xvec, yvec, line1, 'buy')
                yvec = np.append(yvec[1:],0.0)
                xvec = np.append(xvec[1:],0.0)
            if(datas[3] == 2):
                net_shares = net_shares - input_buyvol[row_counter-1]
                net_profit = net_profit + input_buyvol[row_counter-1]*input_buyprice[row_counter-1]
                yvec[-1] = price_avgd
                xvec[-1] = ticker_time[row_counter-1]
                line1 = live_plotter(xvec, yvec, line1, 'sell')
                yvec = np.append(yvec[1:],0.0)
                xvec = np.append(xvec[1:],0.0)
  
ser.close()

#left off:
    #plot wont change color when I get a buy/sell
    #currently have price + 1 on buy to see difference
    #currently need to make datas[3] to datas[2] to trigger buy
    
#LEFT OFF: 
#create loop to perform read


##need to write timestamp in fpga
#test the loopback with the fpga, figure out how to decode incoming serial
#set up this code so that is reads stock data and sends it in real time, test
#build the EMA modules in FPGA
#figure out how to plot data in real time

#for loopback testing, write if statements for sending data back
#ie: if buyprice == 1234.1234 wahtever then send back a buy
