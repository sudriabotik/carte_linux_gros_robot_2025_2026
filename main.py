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

######
## CALAGE DEPART
######
while (node_autom.is_busy()) : 
    time.sleep(0.05)
node_autom.action_safe_position_ascenseur()
while (node_asserv.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_translation(50, 10, 10)
while (node_asserv.is_busy()) :
    time.sleep(0.05)
node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_Y, comm_asserv.Face.FACE_ARRIERE)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_translation(50, 10, 10)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)

logger.log_info("Main", f"Robot position après callage demarage: {robot_state}")

node_autom.action_ready_to_grap()
node_asserv.action_goto_xy(175,1700,comm_asserv.Face.FACE_AVANT)
while (node_asserv.is_busy()) :
    time.sleep(0.05)
node_asserv.action_lookat(175,1200,comm_asserv.Face.FACE_AVANT)
while (node_asserv.is_busy()) :
    time.sleep(0.05)
while (node_autom.is_busy()) : 
    time.sleep(0.05)
node_autom.action_open_pince()

#node_asserv.action_set_linear_speed_accel(100,1)
while (node_asserv.is_busy()) :
    time.sleep(0.05)
node_asserv.action_goto_xy(175,1250,comm_asserv.Face.FACE_AVANT) # trop brutal ici faut changer la decel avant 
while (node_asserv.is_busy()) : 
    time.sleep(0.05)

node_autom.action_grab()
while (node_autom.is_busy()) : 
    time.sleep(0.05)
node_asserv.action_goto_xy(400,800,comm_asserv.Face.FACE_AVANT)
node_autom.action_deposit()

while (node_autom.is_busy()) : 
    time.sleep(0.05)
while (node_asserv.is_busy()) : 
    time.sleep(0.05)
node_autom.action_close_pince()
node_asserv.action_goto_xy(1700,800,comm_asserv.Face.FACE_AVANT)

# ADDED BY CLAUDE: Debug logs to understand why condition doesn't work

while(robot_state.position_x < 750):
    time.sleep(0.05)
node_autom.action_ejecter(2)
'''
## DEBUG 
node_asserv.action_set_linear_speed_accel(50,1)
node_asserv.action_translation(500, 1, 1)
node_autom.action_pos_ax(7,550)


node_autom.action_homing()
node_autom.action_pos_elevator_v(-232) #-232
node_autom.action_pos_elevator_h(-110)
node_autom.action_i2c_servo(2,500)
'''
logger.log_info("Main", "program finished")

# =========================
# STOP LOGGERS (if running)
# =========================
# MODIFIED BY CLAUDE: Stop unified logger if enabled
if canopen_wrapper.unified_logger:
	canopen_wrapper.unified_logger.stop()
	logger.log_info("Main", "Unified logger stopped")

bus.shutdown()
