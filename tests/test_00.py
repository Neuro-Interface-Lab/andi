#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Written by F. Kölbl
# ETIS - University Cergy-Pontoise - CNRS

import andi as ai

NB_dev = ai.nb_connected_devices()
print(NB_dev)
for dev in range(0,NB_dev):
	print(dev)
	print(ai.device_name(dev))
	print(ai.device_SerialNumber(dev))
	if ai.is_opened(dev) == True:
		print('Device already used')
	else:
		print('Device is free :) ')
print(ai.find_first_free_device())

test = ai.Andi()
print('device opened')
test.close()
print('device closed')
