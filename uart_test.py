# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 17:38:54 2020

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


start = int(240)
stop = int(15)
addr = int(0)

sample_buyprice = 1234.5 
buyprice_left = int(sample_buyprice)
buyprice_right= float(str(sample_buyprice-int(sample_buyprice))[1:])
print(buyprice_right)
ratio = (1/65536)
buyprice_right = int((buyprice_right + ratio/2) // ratio * ratio * 65536)
print(buyprice_right)
sample_sellprice = 8765.4321
sellprice_left = int(sample_sellprice)
sellprice_right= float(str(sample_sellprice-int(sample_sellprice))[1:])
sellprice_right = int((sellprice_right + ratio/2) // ratio * ratio * 65536)

sample_buysize = 12.2100
buysize_left = int(sample_buysize)
buysize_right= float(str(sample_buysize-int(sample_buysize))[1:])
buysize_right = int((buysize_right + ratio/2) // ratio * ratio * 65536)

sample_sellsize = 34.4298
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



ser = serial.Serial(port='COM3',baudrate=115200,timeout=(1)) #left usb port on laptop    
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


#while True:
#    if(ser.in_waiting)
#        datas = struct.unpack('>19B', ser.read(19))

datas = struct.unpack('>19B', ser.read(19))
  
  
ser.close()
#counter = 0
#while (counter < 5):
#    current_time = datetime.now()
#    second = current_time.second
#    microsecond = current_time.microsecond


#LEFT OFF: 
#quantize decimal base 16 for decimal values then multiply by 16 before sending
#create loop to perform read
#must change fpga code so it receives least signicant byte first 
#

