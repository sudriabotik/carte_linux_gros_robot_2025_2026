##!/bin/env python3

import can
import can.interfaces.serial.serial_can
import can.interfaces.socketcan.socketcan
import canopen_wrapper
import comm_autom
import comm_asserv
import time

import traceback

import logger

print("attempting to connect to the bus")
# bus : can.BusABC = can.interfaces.serial.serial_can.SerialBus(channel="/dev/ttyACM0", baudrate=500000)
bus = can.Bus(channel="com12", interface="slcan")
print("connected to the network")

canopen_wrapper.instance = canopen_wrapper.CanopenWrapper(bus)

node_autom = None
try :
    node_autom = comm_autom.CanAutomNode(bus, 2)
except Exception as e :
    logger.log_error("Main", f"cannot create autom node, {e}")

node_asserv = None
try :
    node_asserv = comm_asserv.CanAsservNode(bus, 1)
except Exception as e :
    logger.log_error("Main", f"cannot create asserv node, {e}")
    logger.log_traceback(traceback.format_exc())

#node_asserv = comm_asserv.CanAsservNode(network, 1, "./canopen_od/autom.eds") # at the moment, both dictionaries are the same

#node_autom.action_homing(10, 10)

node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : time.sleep(0.05)
node_asserv.action_translation(100, 10, 10)
while (node_asserv.is_busy()) : time.sleep(0.05)
node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_Y, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : time.sleep(0.05)

logger.log_info("Main", "program finished")

"""
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
"""

bus.shutdown()
