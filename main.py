#!/bin/env python3

import canopen
import canopen_wrapper
import comm_autom
import time

print("attempting to connect to the bus")
network = canopen.Network()
network.connect(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
print("connected to the network")

canopen_wrapper.instance = canopen_wrapper.CanopenWrapper(network)

comm_autom = comm_autom.CommAutom(network, 2, "../canopen_od/autom.eds")

time.sleep(1)
# attempts a homing
print("attempting a homing")
comm_autom.action_homing()

time.sleep(5)

print("attempting a grab")
comm_autom.action_grab()

time.sleep(5)