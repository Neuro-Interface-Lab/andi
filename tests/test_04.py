#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by F. Kölbl
# ETIS - University Cergy-Pontoise - CNRS

import andi as ai
import time
import matplotlib.pyplot as plt

#### TEST OF BASIC OUT POSSIBILITIES

# open the first available device
test = ai.Andi()
print('device opened')

# generator param
gene_channel = 1
freq = 1e2
amp = 0.2

# set the generator
test.reset_out(1)
test.enable_out_channel(gene_channel)
test.sine(gene_channel,freq,amp)

# scope param
scope_channel = 0
Vrange = 2.0
Voffset = 0.0
f_sample = 1.0e5
N_samples = int(8194) # no idea why this is not working for N_samples<8194 :(
# set the scope
test.in_enable_channel(scope_channel)
test.in_set_channel(scope_channel,Vrange,Voffset=Voffset)
test.in_configure_channel_record_Nsamples(scope_channel,N_samples,f_sample)

# record with the scope
t, data = test.in_channel_record_Nsamples(scope_channel,N_samples,f_sample,filename='')

# stop all generator channels
test.out_channel_off(-1)
# stop all recording channels
test.in_disable_channel(-1)
# close the device
test.close()
print('device closed')

plt.figure()
plt.plot(t,data)
plt.show()
