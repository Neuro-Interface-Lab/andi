#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by Y. Bornat
# University of Bordeaux - CNRS
"""
This program performs a basic repetitive acquisition just like an
oscilloscope would do...
to run this est program, connect:
    1-, 2- to the groun
    1+, T1 to W1
    2+ to w2
close plot to exit
"""
import andi as ai
import matplotlib.pyplot as plt

active = [True]

def plot_close(event):
    active[0] = False

# open the first available device
with ai.Andi() as test:

    # set the generators
    test.sine(channel=1, freq=500, amp=0.2)
    test.square(channel=0, freq=100, amp=1.65, offset=1.65, symmetry=0.05)

    #set acquisition parameters
    test.in_set_channel(channel=1, Vrange=5, Voffset=0)
    test.in_set_channel(channel=0, Vrange=5, Voffset=0)
    test.set_Ext_trigger(source=0, type="Rising", ref="left", position=0)
    t = test.set_acq(freq=1000000, samples=8000)


    fig = plt.figure()
    plt.ion()
    dat0, dat1 = test.acq()
    line0, = plt.plot(t, dat0)
    line1, = plt.plot(t, dat1)
    fig.canvas.mpl_connect('close_event', plot_close)
    
    while(active[0]):
        dat0, dat1 = test.acq()
        line0.set_ydata(dat0)
        line1.set_ydata(dat1)
        fig.canvas.draw_idle()
        plt.pause(0.000001) 
    


