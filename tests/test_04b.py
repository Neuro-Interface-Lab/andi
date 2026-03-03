#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by Y. Bornat
# University of Bordeaux - CNRS
""""
This program performs data recording on channel 0.
No specific setup is required

it seems that 250kHz/275kHz is the best rate the system can perform without
issue (at least on my computer, YB) even if real troubles come around 700kHz.
"""

import andi as ai
import matplotlib.pyplot as plt

# open the first available device
with ai.Andi() as test:

    # scope param
    test.in_set_channel(channel=0, Vrange=5, Voffset=0, attenuation=1.0)

    # record with the scope
    t, data = test.record(channel=0, freq=250000, time=100.0)

plt.figure()
plt.plot(t,data)
plt.show()
