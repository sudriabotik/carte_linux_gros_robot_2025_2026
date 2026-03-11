#!/bin/env python3

import canopen
import canopen_wrapper
import comm_autom
import comm_asserv
import time

import logger

print("attempting to connect to the bus")
network = canopen.Network()
network.connect(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
print("connected to the network")

canopen_wrapper.instance = canopen_wrapper.CanopenWrapper(network)

node_autom = None
try :
    node_autom = comm_autom.CanAutomNode(network, 2, "./canopen_od/autom.eds")
except Exception as e :
    logger.log_error("Main", f"cannot create autom node, {e}")

node_asserv = None
try :
    node_asserv = comm_asserv.CanAsservNode(network, 1, "./canopen_od/autom.eds")
except Exception as e :
    logger.log_error("Main", f"cannot create asserv node, {e}")

#node_asserv = comm_asserv.CanAsservNode(network, 1, "./canopen_od/autom.eds") # at the moment, both dictionaries are the same

time.sleep(1)
# attempts a homing
if node_autom != None :
    print("attempting a homing")
    node_autom.action_homing()

time.sleep(5)


if node_asserv != None :
    print("doing a small translation")
    node_asserv.action_translation(0, 10, 1)

    print("waiting for the translation to finish")
    while node_asserv.is_busy() :
        time.sleep(0.01)
    print("translation finished")

if node_autom != None :
    print("small wait before the grab")
    time.sleep(1)

    print("attempting a grab")
    node_autom.action_grab()

time.sleep(5)