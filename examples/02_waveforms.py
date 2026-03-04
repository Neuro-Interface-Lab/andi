#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by F. Kölbl
# ETIS - University Cergy-Pontoise - CNRS

import andi as ai
import time

#### TEST OF BASIC OUT POSSIBILITIES

# open the first available device
test = ai.Andi()
print('device opened')

# reset all the generators
test.reset_out(1)
# count the number of out channels
print('the number of out-channels is: '+str(test.out_channel_count()))

channel = 1
# enable the channel and check if done
test.enable_out_channel(channel)
print('Channel is enable: '+str(test.is_out_channel_enable(channel)))
# # get the frequency infos of the channel
#test.out_set_function(channel,'Sine')
#test.out_set_freq(channel,1e3)
# print(test.out_get_freq(channel))
test.sine(channel,1e3,1)
time.sleep(10)
test.square(channel,1e3,1)
time.sleep(10)
test.triangle(channel,1e3,1)

# wait for a certain amount of time...
time.sleep(10)


# # disable the channel and check if done
# test.disable_out_channel(channel)
# print('Channel is enable: '+str(test.is_out_channel_enable(channel)))

test.close()
print('device closed')
