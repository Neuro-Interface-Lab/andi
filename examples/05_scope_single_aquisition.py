#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by Y. Bornat
# University of Bordeaux - CNRS
""""
This program performs a basic single acquisition just like an
oscilloscope would do...
to run this est program, connect:
    1-, 2- to the groun
    1+, T1 to W1
    2+ to w2
"""

import andi as ai
import matplotlib.pyplot as plt
import time


# open the first available device
with ai.Andi() as test:
    # set the generators
    test.sine(channel=1, freq=500, amp=0.2)
    test.square(channel=0, freq=100, amp=1.65, offset=1.65, symmetry=0.05)

    #set acquisition parameters
    test.in_set_channel(channel=1, Vrange=5, Voffset=0)
    test.in_set_channel(channel=0, Vrange=5, Voffset=0)
    test.set_Ext_trigger(source=0, type="Rising", ref="left border", position=0)
    t = test.set_acq(freq=1000000, samples=8000)

    #actually perform acquisition
    dat0, dat1 = test.acq()
    #use this line instead if you need higher precision and signal is periodic
    #dat0, dat1 = test.acq(avg=10, quantum=0.0001)
    

plt.figure()
plt.plot(t, dat0)
plt.plot(t, dat1)    
plt.show()
