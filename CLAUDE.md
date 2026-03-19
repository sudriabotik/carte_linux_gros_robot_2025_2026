# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a robotics control system for the "gros robot" competition robot (2025-2026). The system communicates with embedded controllers via CANopen protocol over CAN bus to control actuators (automation node) and motion (asserv/odometry node).

## Architecture

### Communication Stack

The system uses a custom "Action Comm" protocol built on top of CANopen:

1. **canopen_wrapper.py**: Low-level CANopen communication
   - Handles RPDO (Receive PDO - commands to nodes) and TPDO (Transmit PDO - status from nodes)
   - `request_action()` sends action commands via two RPDOs containing action_id, 6 parameters, and command_id
   - Decodes TPDOs using configurable byte slot mappings
   - Uses COB-IDs for message routing (4-bit function code + 7-bit node ID)

2. **action_comm_node.py**: Base class for CANopen nodes
   - `CanActionNode` provides common infrastructure for all nodes
   - `_CanActionNodeReader` (CAN Listener) monitors TPDO0 for status updates
   - Tracks: current_command_status, current_command_id, current_action_id, last_completed_command_id, command_error_code
   - `is_busy()` checks if node is executing a command (status != RUNNING)

3. **comm_autom.py**: Automation node interface (node_id=2)
   - Controls elevator and grabber mechanisms
   - Actions: homing, grab, pos_elevator_h, pos_elevator_v

4. **comm_asserv.py**: Motion control node interface (node_id=1)
   - Controls robot movement and positioning
   - Actions: set speeds/accelerations (linear/angular), goto_xy, translation, recalibration
   - Enums: Face (AVANT/ARRIERE), Facing (direction for recalibration)

### Support Modules

- **robot_comm_data.py**: Shared constants for command status codes and error codes (CMD_STATUS_*, CMD_ERROR_*)
- **logger.py**: Timestamped logging with levels (VERB, INFO, WARN, ERR, TRCBCK)
- **constants.py**: Team enum (TEAM_B, TEAM_Y)

## Running the Code

### CAN Bus Configuration

The code supports two CAN interfaces:

**Linux (SocketCAN):**
```python
bus = can.Bus(channel="can0", interface="socketcan")
```

**Windows/Serial (via USB-CAN adapter):**
```python
bus = can.interfaces.serial.serial_can.SerialBus(channel="COM11", baudrate=500000)
```

Note: Change the channel in main.py:17 based on your platform. On Windows, use device manager to identify the correct COM port.

### Execution

```bash
python3 main.py
```

The main.py currently:
1. Initializes CAN bus connection
2. Creates CanAsservNode (node_id=1) and CanAutomNode (node_id=2)
3. Polls asserv node status in infinite loop

## Key Implementation Details

### Action Request Flow

When you call an action method (e.g., `node_asserv.action_translation()`):

1. Action method calls `canopen_wrapper.instance.request_action(node_id, action_id, params)`
2. Wrapper sends RPDO1 with [action_id(16bit), param1(16bit), param2(16bit), param3(16bit)]
3. Wrapper sends RPDO2 with [param4(16bit), param5(16bit), param6(16bit), command_id(16bit)]
4. Node processes action and sends TPDO0 status updates
5. `_CanActionNodeReader` listener updates status variables
6. Poll `is_busy()` to wait for completion

### Byte Packing Bug

**CRITICAL BUG in canopen_wrapper.py:120-145**: The bit shift operations are incorrect.

Lines like `(action_id << 8) & 0xFF` shift left then mask, which loses the upper byte. Should be `(action_id >> 8) & 0xFF` to extract the high byte.

This affects both RPDO data preparation sections (lines 117-127 and 135-145). The second RPDO also incorrectly uses param_resized[0:2] instead of param_resized[3:5].

## Common Pitfalls

- The `canopen_wrapper.instance` is a global singleton that must be initialized before creating any node objects
- Node constructors require the CAN bus object to create listeners
- Threading: Each CanActionNode creates a listener on a separate thread via can.Notifier
- The `is_busy()` check currently only considers status==1 (RUNNING) as not busy, which may be inverted logic
