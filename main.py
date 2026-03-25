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
import uart_logger  # DEPRECATED - kept for backwards compatibility
import can_logger   # DEPRECATED - kept for backwards compatibility
import unified_logger  # ADDED BY CLAUDE: Unified UART+CAN logger

# =========================
# CONFIGURATION DEBUG
# =========================
DEBUG_UART = True                  # Enable UART debug logging from microcontroller
DEBUG_CAN_CHANGES_ONLY = True      # Log CAN messages only when values change
DEBUG_CAN_LOG_TO_FILE = True       # DEPRECATED - use DEBUG_UNIFIED_LOGGER instead
DEBUG_UNIFIED_LOGGER = True        # ADDED BY CLAUDE: Enable unified UART+CAN logging to single file

print("attempting to connect to the bus")
bus = can.interface.Bus(bustype='slcan', channel='/dev/ttyACM0', bitrate=500000)
print("connected to the network")

# Set CAN debug configuration before creating wrapper
canopen_wrapper.DEBUG_CAN_CHANGES_ONLY = DEBUG_CAN_CHANGES_ONLY

# ADDED BY CLAUDE: Start unified logger if enabled (replaces separate UART and CAN loggers)
if DEBUG_UNIFIED_LOGGER:
	canopen_wrapper.unified_logger = unified_logger.UnifiedLogger(
		uart_port="/dev/ttyS2",
		uart_baudrate=1000000,
		log_dir="log"
	)
	canopen_wrapper.unified_logger.start()
	logger.log_info("Main", "Unified logger (UART+CAN) started")

# Legacy separate loggers (DEPRECATED - only used if unified logger is disabled)
else:
	# Start CAN file logger if enabled
	if DEBUG_CAN_LOG_TO_FILE:
		canopen_wrapper.can_file_logger = can_logger.CanLogger(log_dir="log_can")
		canopen_wrapper.can_file_logger.start()
		logger.log_info("Main", "CAN file logger started")

	# Start UART logger if enabled
	uart_log = None
	if DEBUG_UART:
		uart_log = uart_logger.UartLogger(port="/dev/ttyS2", baudrate=1000000, log_dir="log")
		uart_log.start()
		logger.log_info("Main", "UART logger started")

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
    #logger.log_traceback(traceback.format_exc())

#node_asserv = comm_asserv.CanAsservNode(network, 1, "./canopen_od/autom.eds") # at the moment, both dictionaries are the same

#node_autom.action_homing(10, 10)

node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : time.sleep(0.05)
node_asserv.action_translation(100, 10, 10)
while (node_asserv.is_busy()) : time.sleep(0.05)
node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_Y, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : time.sleep(0.05)
node_asserv.action_translation(300, 10, 10)
while (node_asserv.is_busy()) : time.sleep(0.05)
node_asserv.action_goto_xy(500,1000,comm_asserv.Face.FACE_AVANT)
while (node_asserv.is_busy()) : time.sleep(0.05)

'''
node_autom.action_homing()
node_autom.action_grab()

node_autom.action_deposit()
node_autom.action_ejecter(2)


## DEBUG 
node_autom.action_pos_elevator_v(-232) #-232
node_autom.action_pos_elevator_h(-110)
node_autom.action_i2c_servo(2,500)
'''
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

# =========================
# STOP LOGGERS (if running)
# =========================
# MODIFIED BY CLAUDE: Stop unified logger if enabled
if canopen_wrapper.unified_logger:
	canopen_wrapper.unified_logger.stop()
	logger.log_info("Main", "Unified logger stopped")

# Legacy separate loggers cleanup (DEPRECATED)
if uart_log:
	uart_log.stop()
	logger.log_info("Main", "UART logger stopped")

if canopen_wrapper.can_file_logger:
	canopen_wrapper.can_file_logger.stop()
	logger.log_info("Main", "CAN file logger stopped")

bus.shutdown()
