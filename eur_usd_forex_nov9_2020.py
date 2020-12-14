# -*- coding: utf-8 -*-
"""


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

ser = serial.Serial(port='COM3',baudrate=115200,timeout=(.1)) #left usb port on laptop 

#send the data to uart in real time
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
    

#plot the datas
def live_plotter(x_vec,y1_data,xvec1,yvec1,xvec2,yvec2,line1,line2,line3,inputter,identifier='',pause_time=0.0000001):
    if line1==[]:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13,6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec,y1_data,'-.',alpha=0.8, color = 'blue')
        line2, = ax.plot(xvec1,yvec1,'s',alpha = 0.8, color = 'green')
        line3, = ax.plot(xvec2,yvec2,'s',alpha = 0.8, color = 'red')
        #update plot label/title
        plt.ylabel('Price')
        plt.xlabel('time (s)')
        plt.title('EUR-USD November 9-2020 Net Profit=$%.2f Net Shares=%.2f Compute Time=%d ns' % (live_plotter.profit, live_plotter.shares, live_plotter.timestamp))
        plt.show()
    # after the figure, axis, and line are created, we only need to update the y-data
    if(inputter == 'avg price'):
        line1.set_ydata(y1_data)
        line1.set_xdata(x_vec)
        plt.title('EUR-USD November 9-2020 Net Profit=$%.2f Net Shares=%.2f Compute Time=%d ns' % (live_plotter.profit, live_plotter.shares, live_plotter.timestamp))
    if(inputter == 'buy'):
        line2.set_ydata(yvec1)
        line2.set_xdata(xvec1)
    if(inputter == 'sell'):
        line3.set_ydata(yvec2)
        line3.set_xdata(xvec2)
    # adjust limits if new data goes beyond bounds
    #if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
    if(inputter == 'avg price'):
        plt.ylim([np.min(y1_data)-(.0001),np.max(y1_data)+(.0001)])    
        if np.min(x_vec)<=line1.axes.get_xlim()[0] or np.max(x_vec)>=line1.axes.get_xlim()[1]:
            plt.xlim([np.min(x_vec),np.max(x_vec)+np.std(x_vec)])    
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    # return line so we can update it again in the next iteration
    return line1,line2,line3

# MAIN FUNCTION ######################################
init_time = time.perf_counter()
init_avg_price = (input_sellprice[0] + input_buyprice[0])/2
row_counter = 0
line1 = []
line2 = []
line3 = []
yvec = np.array([init_avg_price]*700)
xvec = np.array([0]*700)
yvec1 = np.array([init_avg_price]*700)
xvec1 = np.array([0]*700)
yvec2 = np.array([init_avg_price]*700)
xvec2 = np.array([0]*700)
live_plotter.shares = 0.0000
live_plotter.profit = 0.0000
live_plotter.timestamp = 0.0000;
timestamper = [0]*4;
while True:
    current_time = time.perf_counter() - init_time
    if(current_time > ticker_time[row_counter]): #time to send a message out
        send_data(input_sellprice[row_counter], input_buyprice[row_counter],
                  input_sellvol[row_counter], input_buyvol[row_counter])
        price_avgd = (input_sellprice[row_counter] + input_buyprice[row_counter])/2
        #updated plot price:
        yvec[-1] = price_avgd
        xvec[-1] = ticker_time[row_counter]
        line1,line2,line3 = live_plotter(xvec, yvec,xvec1,yvec1,xvec2,yvec2, line1,line2,line3, 'avg price')
        yvec = np.append(yvec[1:],0.0)
        xvec = np.append(xvec[1:],0.0)
        row_counter = row_counter + 1
        
        if(ser.in_waiting > 0): #msg was sent out and 100ms has passed, check for data
            datas = [0]*19
            numbytes = ser.in_waiting
            #datas = struct.unpack('>19B', ser.read(19))
            z = '>'; zz = 'B'
            numbyte_string = z + str(numbytes) + zz
            datas = struct.unpack(numbyte_string, ser.read(numbytes))
            #plot the buy/sell
            #buysell byte => 1 buy, 2 sell
            if(datas[2] == 1):
                live_plotter.shares = live_plotter.shares + input_sellvol[row_counter-1]
                live_plotter.profit = live_plotter.profit - input_sellvol[row_counter-1]*input_sellprice[row_counter-1]
                timestamper[0] = datas[6]<<24;
                timestamper[1] = datas[5]<<16;
                timestamper[2] = datas[4]<<8;
                timestamper[3] = datas[3];
                live_plotter.timestamp = 20 * sum(timestamper)
                yvec1[-1] = price_avgd
                xvec1[-1] = ticker_time[row_counter-1]
                line1,line2,line3 = live_plotter(xvec, yvec,xvec1,yvec1,xvec2,yvec2, line1,line2,line3, 'buy')
                yvec1 = np.append(yvec1[1:],0.0)
                xvec1 = np.append(xvec1[1:],0.0)
            if(datas[2] == 2):
                live_plotter.shares = live_plotter.shares - input_buyvol[row_counter-1]
                live_plotter.profit = live_plotter.profit + input_buyvol[row_counter-1]*input_buyprice[row_counter-1]
                timestamper[0] = datas[6]<<24;
                timestamper[1] = datas[5]<<16;
                timestamper[2] = datas[4]<<8;
                timestamper[3] = datas[3];
                live_plotter.timestamp = 20 * sum(timestamper)
                yvec2[-1] = price_avgd
                xvec2[-1] = ticker_time[row_counter-1]
                line1,line2,line3 = live_plotter(xvec, yvec,xvec1,yvec1,xvec2,yvec2, line1,line2,line3, 'sell')
                yvec2 = np.append(yvec2[1:],0.0)
                xvec2 = np.append(xvec2[1:],0.0)
        
    else: #nothing to do, check for data again
        if(ser.in_waiting > 0):
            datas = [0]*19
            numbytes = ser.in_waiting
            #datas = struct.unpack('>19B', ser.read(19))
            z = '>'; zz = 'B'
            numbyte_string = z + str(numbytes) + zz
            datas = struct.unpack(numbyte_string, ser.read(numbytes))
            #plot the buy/sell
            #buysell byte => 1 buy, 2 sell
            if(datas[2] == 1):
                live_plotter.shares = live_plotter.shares + input_sellvol[row_counter-1]
                live_plotter.profit = live_plotter.profit - input_sellvol[row_counter-1]*input_sellprice[row_counter-1]
                timestamper[0] = datas[6]<<24;
                timestamper[1] = datas[5]<<16;
                timestamper[2] = datas[4]<<8;
                timestamper[3] = datas[3];
                live_plotter.timestamp = 20 * sum(timestamper)
                yvec1[-1] = price_avgd
                xvec1[-1] = ticker_time[row_counter-1]
                line1,line2,line3 = live_plotter(xvec, yvec,xvec1,yvec1,xvec2,yvec2, line1,line2,line3, 'buy')
                yvec1 = np.append(yvec1[1:],0.0)
                xvec1 = np.append(xvec1[1:],0.0)
            if(datas[2] == 2):
                live_plotter.shares = live_plotter.shares - input_buyvol[row_counter-1]
                live_plotter.profit = live_plotter.profit + input_buyvol[row_counter-1]*input_buyprice[row_counter-1]
                timestamper[0] = datas[6]<<24;
                timestamper[1] = datas[5]<<16;
                timestamper[2] = datas[4]<<8;
                timestamper[3] = datas[3];
                live_plotter.timestamp = 20 * sum(timestamper)
                yvec2[-1] = price_avgd
                xvec2[-1] = ticker_time[row_counter-1]
                line1,line2,line3 = live_plotter(xvec, yvec,xvec1,yvec1,xvec2,yvec2, line1,line2,line3, 'sell')
                yvec2 = np.append(yvec2[1:],0.0)
                xvec2 = np.append(xvec2[1:],0.0)
  
ser.close()

    
#LEFT OFF: 

##need to write timestamp in fpga
#test the loopback with the fpga, figure out how to decode incoming serial
#set up this code so that is reads stock data and sends it in real time, test
#build the EMA modules in FPGA
#figure out how to plot data in real time

#for loopback testing, write if statements for sending data back
#ie: if buyprice == 1234.1234 wahtever then send back a buy
