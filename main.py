#!/bin/env python3

import can
import can.interfaces.serial.serial_can
import can.interfaces.socketcan.socketcan
import canopen_wrapper
import comm_autom
import comm_asserv
import time

import traceback
import logger
import unified_logger  # ADDED BY CLAUDE: Unified UART+CAN logger
import robot  # ADDED BY CLAUDE: Robot state management

# =========================
# CONFIGURATION DEBUG
# =========================
DEBUG_CAN_CHANGES_ONLY = True      # Log CAN messages only when values change
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

# ADDED BY CLAUDE: Create Robot instance to track robot position from TPDO[1]
# Position will be automatically updated at 10Hz from asserv node odometry
robot_state = robot.Robot(node_asserv, node_autom)
logger.log_info("Main", f"Robot state initialized: {robot_state}")

# ADDED BY CLAUDE: Connect robot to asserv node for automatic position updates
if node_asserv:
    node_asserv.can_reader.robot = robot_state
    logger.log_info("Main", "Robot position tracking enabled via TPDO[1]")

#node_asserv = comm_asserv.CanAsservNode(network, 1, "./canopen_od/autom.eds") # at the moment, both dictionaries are the same

#node_autom.action_homing(10, 10)

time.sleep(0.200) # pour bien avoir tous le debut des logs. 

node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_translation(100, 10, 10)
while (node_asserv.is_busy()) :
    time.sleep(0.05)
node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_Y, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_translation(300, 10, 10)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)

logger.log_info("Main", f"Robot position: {robot_state}")

node_asserv.action_goto_xy(175,750,comm_asserv.Face.FACE_AVANT)
while (node_asserv.is_busy()) :
    time.sleep(0.05)
node_autom.action_open_pince()
while (node_autom.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_goto_xy(175,450,comm_asserv.Face.FACE_AVANT)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)

node_autom.action_grab()
while (node_autom.is_busy()) : 
    time.sleep(0.05)
node_autom.action_deposit()
while (node_autom.is_busy()) : 
    time.sleep(0.05)

node_asserv.action_goto_xy(1200,450,comm_asserv.Face.FACE_AVANT)
# ADDED BY CLAUDE: Debug logs to understand why condition doesn't work
logger.log_info("Main", f"Starting goto_xy(1200,450), waiting for X < 800. Current position: {robot_state}")
while(robot_state.position_x < 800):
    logger.log_info("Main", f"Still waiting (X < 800)... Current position: {robot_state}")
    time.sleep(0.05)

logger.log_info("Main", f"Condition met (X >= 800)! Final position: {robot_state}")
node_autom.action_ejecter(2)


node_asserv.action_set_linear_speed_accel(100,50)
node_asserv.action_translation(-2500, 1, 1)
'''
## DEBUG 
node_autom.action_homing()
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

bus.shutdown()
