#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by Y. Bornat
# University of Bordeaux - CNRS
"""
This program performs a basic repetitive acquisition just like an
oscilloscope would do... to improve precision, several acquisitions
are averaged. The resulting display is showed in real time, so it is
possible to navigate while the acquisitions are running
to run this est program, connect:
    1-, 2- to the groun
    1+, T1 to W1
    2+ to w2
scroll to update the sampling frequency
center-click to give up previously acquired data
close window to exit
"""
import andi as ai
import matplotlib.pyplot as plt

active = [True]
nb_avg = 1
sfreq  = [10000000]
refresh= [False]

def plot_close(event):
    active[0] = False
def scroll_evt(event):
    if event.button == 'up':
        sfreq[0]/=2
    if event.button == 'down':
        sfreq[0]*=2
        if sfreq[0]>100000000:
            sfreq[0]=100000000
    print("New frequency {}Hz".format(sfreq[0]))
    refresh[0]=True
def bt_evt(event):
    if event.button==2:
        refresh[0]=True

# open the first available device
with ai.Andi() as test:

    # set the generators
    test.sine(channel=1, freq=5000, amp=0.002)
    test.square(channel=0, freq=1000, amp=1.65, offset=1.65, symmetry=0.05)

    #set acquisition parameters
    test.in_set_channel(channel=1, Vrange=5, Voffset=0)
    test.in_set_channel(channel=0, Vrange=5, Voffset=0)
    test.set_Ext_trigger(source=0, type="Rising", ref="left", position=0)
    t = test.set_acq(freq=sfreq[0], samples=8192)


    fig = plt.figure()
    plt.ion()
    dat0, dat1 = test.acq()
    line0, = plt.plot(t, dat0)
    line1, = plt.plot(t, dat1)
    fig.canvas.mpl_connect('close_event', plot_close)
    fig.canvas.mpl_connect('scroll_event', scroll_evt)
    fig.canvas.mpl_connect('button_press_event', bt_evt)
    
    while(active[0]):
        for i in range(10):
            d0, d1 = test.acq()
            dat0+=d0
            dat1+=d1
            nb_avg+=1
        line0.set_ydata(dat0/nb_avg)
        line1.set_ydata(dat1/nb_avg)
        fig.canvas.draw_idle()
        plt.pause(0.000001)
        #event management is performed during the previous pause
        if refresh[0]:
            t = test.set_acq(freq=sfreq[0], samples=8192)
            dat0*=0
            dat1*=0
            nb_avg=0
            line0.set_xdata(t)
            line1.set_xdata(t)
            refresh[0]=False
        #after a while, simply behave like a lowpass filter
        if nb_avg>30000:
            new_avg = nb_avg - 1000
            dat0*=new_avg/nb_avg
            dat1*=new_agv/nb_avg
            nb_avg = new_avg
    
print(nb_avg)

