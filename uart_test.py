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

total bytes per transaction: 19

@author: mecap
"""

import serial
import datetime

ser = serial.Serial('COM3', 115200, databits=8, parity='none',stopbits=1) #left usb port on laptop
start = int(240)
stop = int(15)
addr = int(0)

sample_buyprice = 1234.9678
buyprice_left = int(sample_buyprice)
buyprice_right= float(str(sample_buyprice-int(sample_buyprice))[1:])
buyprice_right = int(buyprice_right*10000)

sample_sellprice = 8765.4321
sellprice_left = int(sample_sellprice)
sellprice_right= float(str(sample_sellprice-int(sample_sellprice))[1:])
sellprice_right = int(sellprice_right*10000)

sample_buysize = 0012.2100
buysize_left = int(sample_buysize)
buysize_right= float(str(sample_buysize-int(sample_buysize))[1:])
buysize_right = int(buysize_right*10000)

sample_sellsize = 0034.4298
sellsize_left = int(sample_sellsize)
sellsize_right= float(str(sample_sellsize-int(sample_sellsize))[1:])
sellsize_right = int(sellsize_right*10000)


ser.write(bytes(start))
ser.write(bytes(addr))
ser.write(buyprice_left.to_bytes(2, 'little'))
ser.write(buyprice_right.to_bytes(2, 'little'))
ser.write(sellprice_left.to_bytes(2, 'little'))
ser.write(sellprice_right.to_bytes(2, 'little'))
ser.write(buysize_left.to_bytes(2,'little'))
ser.write(buysize_right.to_bytes(2, 'little'))
ser.write(sellsize_left.to_bytes(2, 'little'))
ser.write(sellsize_right.to_bytes(2, 'little'))
ser.write(bytes(stop))

ser.close()
#counter = 0
#while (counter < 5):
#    current_time = datetime.now()
#    second = current_time.second
#    microsecond = current_time.microsecond





