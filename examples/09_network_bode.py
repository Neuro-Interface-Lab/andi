#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by F. Kolbl
# CY University - CNRS
"""
This program performs basic network caracterisation
(Bode plot) of a DUT.
to run this test program, connect: 
	1-, 2- to ground
	
"""
import andi as ai
import matplotlib.pyplot as plt

# open the first available device
with ai.Andi() as test:
	test.configure_network_analyser()
	freq, gain, phase = test.bode_measurement(1e3, 1e6, n_points = 201, dB = True, deg = True)
        #calling test.close() is not necessary, it is implicitly performed when exiting the context manager

plt.figure()
plt.subplot(211)
plt.semilogx(freq, gain)
plt.subplot(212)
plt.semilogx(freq, phase)
plt.show()
