# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 22:36:09 2020

@author: mecap
"""

import matplotlib.pyplot as plt
import numpy as np

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')

def live_plotter(x_vec,y1_data,line1,line2,identifier='',pause_time=1):
    if line1==[]:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13,6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec,y1_data,'-o',alpha=0.8, color = 'green')
        line2, = ax.plot(x_vec,y1_data,'s',color = 'red')
        #update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()
    
    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    line1.set_xdata(x_vec)
    if x % 2 == 0:
        line2.set_ydata(y1_data)
        line2.set_xdata(x_vec)
    #adjust limits if new data goes beyond bounds
    if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(x1_data)>=line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data)-(.0001),np.max(y1_data)+(.0001)])
        
    if np.min(x_vec)<=line1.axes.get_xlim()[0] or np.max(x_vec)>=line1.axes.get_xlim()[1]:
       plt.xlim([np.min(x_vec)-np.std(x_vec),np.max(x_vec)+np.std(x_vec)])    
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    
    # return line so we can update it again in the next iteration
    return line1, line2


counter = 0
size = 100
x_vec = np.linspace(0,1,size+1)[0:-1]
y_vec = np.random.randn(len(x_vec))
line1 = []
line2 = []
x = 0
while True:
    x = x + 1
    counter = counter + 1
    rand_val = np.random.randn(1)
    x_vec[-1] = counter
    y_vec[-1] = rand_val
    line1, line2 = live_plotter(x_vec,y_vec,line1, line2)
    y_vec = np.append(y_vec[1:],0.0)