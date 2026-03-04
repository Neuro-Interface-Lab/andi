#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by F. Kölbl
# ETIS - University Cergy-Pontoise - CNRS

import andi as ai

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
# get the frequency infos of the channel
F_channel = test.out_frequency_info(channel)
print('The channel can generate frequencies from '+str(F_channel[0])+'Hz to '+str(F_channel[1])+'Hz')
D_channel = test.out_data_info(channel)
print('The channel can generate a signal from  '+str(D_channel[0])+' samples to '+str(D_channel[1])+' samples')
print(D_channel[1]/D_channel[0])
T_channel = test.out_run_info(channel)
print('The channel can generate a signal from  '+str(T_channel[0])+' sec. to '+str(T_channel[1])+' sec.')


# disable the channel and check if done
test.disable_out_channel(channel)
print('Channel is enable: '+str(test.is_out_channel_enable(channel)))

test.close()
print('device closed')
