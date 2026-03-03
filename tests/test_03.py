#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by F. Kölbl
# ETIS - University Cergy-Pontoise - CNRS

import andi as ai
import time

#### TEST OF BASIC IN POSSIBILITIES

# open the first available device
test = ai.Andi()
print('device opened')

print('Number of available recording channels: '+str(test.in_channel_count()))
F_info = test.in_frequency_info()
print('The min ADC sampling frequency is: '+str(F_info[0]))
print('The max ADC sampling frequency is: '+str(F_info[1]))
print('The current ADC sampling frequency is: '+str(test.in_sampling_freq_get()))
print('The ADC has an output of '+str(test.in_bits_info())+' bits')
S_info = test.in_buffer_size_info()
print('The min buffer size is: '+str(S_info[0]))
print('The max buffer size is: '+str(S_info[1]))
print('The current buffer size is: '+str(test.in_buffer_size_get()))

# infos on channel 0
channel = 0
test.in_enable_channel(channel)
range_info = test.in_channel_range_info(channel)
print('Channel 0 has a minimum input range of '+str(range_info[0]))
print('Channel 0 has a maximum input range of '+str(range_info[1]))
print('Channel 0 has an input range number of steps of '+str(range_info[2]))
offset_info = test.in_channel_offset_info(channel)
print('Channel 0 has a minimum offset of '+str(offset_info[0]))
print('Channel 0 has a maximum offset of '+str(offset_info[1]))
print('Channel 0 has an offset number of steps of '+str(range_info[2]))
print('The current input range is '+str(test.in_channel_range_get(channel))+' V')
print('The current offset is '+str(test.in_channel_offset_get(channel))+' V')
print('The current attenuation is '+str(test.in_channel_attenuation_get(channel)))
test.in_disable_channel(channel)

# close the device
test.close()
print('device closed')
