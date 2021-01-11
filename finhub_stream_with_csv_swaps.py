# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 20:08:59 2020

THIS ONE SWAPS OUT CSV FILES AT MIDNIGHT
FINHUB WEBSOCKET STREAM, CAN BE USED FOR US STOCKS, FOREX, CRYPTO
@author: mecap
"""
#USE THIS FOR CRYPTOS AND FOREX

#https://pypi.org/project/websocket_client/
import websocket
import csv
import json
import pandas
import pandas.io.json as pd_json
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)	
global data_file
data_file = open("C:/Users/mecap/Desktop/600/bitcoin_data.csv", mode='w')
data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
data_writer.writerow(["c", "p", "s", "t", "v", dt_string])
global old_day 
old_day = now.strftime("%d")

def on_message(ws, message):
    global new_day
    global old_day
    global data_file

 
    xyz = str(message)
    data_object = json.loads(xyz)
    po = pd_json.json_normalize(data_object, record_path='data')
    po.to_csv(data_file, index=False, header=False, line_terminator='\n')

        
    now = datetime.now()
    new_day = now.strftime("%d")
    
    if(new_day != old_day):
        #swap out csv files
        data_file.close()
        data_file = open("C:/Users/mecap/Desktop/600/bitcoin_data"+new_day+".csv", mode='w')
        old_day = new_day

    
def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")
    
    # dd/mm/YY H:M:S
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    data_writer.writerow(["c", "p", "s", "t", "v", dt_string])	
    data_file.close()

        
def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"TSLA"}')
    ws.send('{"type":"subscribe","symbol":"AMZN"}')
    #ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=bvlu2gv48v6vvdqtetl0",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()