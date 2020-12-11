# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 13:34:23 2020

@author: mecap
"""

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import time

api_key = 'CULIE415UXKQ7BN4'

ts = TimeSeries(key=api_key, output_format='pandas')
print(data)

i = 1

#while i ==1:
 #   data, meta_data = ts.get_intraday(symbol='MSFT', interval = '1min', outputsize = 'full')
  #  data.to_excel("finance_api.xlsx")
   # time.sleep(60)
    
close_data = data['4. close']
percent_change = close.data.pct_change()
print(percent_change)

last_change = percent_change[-1]

if abs(last