"""
Unified Logger Module - Merges UART and CAN logs into a single timestamped file

This module provides a unified logger that combines UART data and CAN messages
(both TX and RX) into a single chronologically-ordered log file with tags:
- [UART] for UART data from microcontroller
- [CAN TX] for CAN messages sent to nodes
- [CAN RX] for CAN messages received from nodes

All timestamps use the unified clock from logger.py for perfect synchronization.
"""
'''
import serial
import threading
import time
import os
import datetime
import core.interface.log_management.logger as logger


class UnifiedLogger:
	"""
	Unified logger that combines UART and CAN data into a single log file.

	Writes all debug data to a single timestamped file in log/ directory.
	Thread-safe for concurrent access from UART thread and CAN message handlers.
	"""

	def __init__(self, uart_port_asserv="/dev/ttyS2", uart_port_autom="/dev/ttyS6", uart_baudrate=1000000, log_dir="log"):
		"""
		Initialize the unified logger.

		:param uart_port_asserv: UART port for ASSERV (default: /dev/ttyS2)
		:param uart_port_autom: UART port for AUTOM (default: /dev/ttyS6)
		:param uart_baudrate: UART baudrate (default: 1000000)
		:param log_dir: Directory to store log files (default: "log")
		"""
		# Deux ports UART distincts
		self.uart_port_asserv = uart_port_asserv
		self.uart_port_autom = uart_port_autom
		self.uart_baudrate = uart_baudrate
		self.log_dir = log_dir

		# Thread control for UART listeners
		self.running = False

		# Deux threads séparés
		self.uart_thread_asserv = None
		self.uart_thread_autom = None

		# Serial port and log file handles
		# Deux ports série séparés
		self.serial_port_asserv = None
		self.serial_port_autom = None
		self.log_file = None
		self.log_filename = None

		# Thread-safe file writing (shared lock for UART threads and CAN callbacks)
		self.lock = threading.Lock()

		self.enabled = False

		# Create log directory if it doesn't exist
		if not os.path.exists(self.log_dir):
			os.makedirs(self.log_dir)
			logger.log_info("UnifiedLogger", f"Created log directory: {self.log_dir}")


	def start(self):
		"""
		Start the unified logger.
		Opens UART port, creates timestamped log file, and starts UART listener thread.
		"""
		if self.enabled:
			logger.log_warning("UnifiedLogger", "Unified logger already started")
			return

		# Open UART serial port ASSERV
		try:
			self.serial_port_asserv = serial.Serial(
				port=self.uart_port_asserv,
				baudrate=self.uart_baudrate,
				timeout=0.1  # Non-blocking with small timeout
			)
			logger.log_info("UnifiedLogger", f"Opened UART ASSERV on {self.uart_port_asserv} @ {self.uart_baudrate} baud")
		except Exception as e:
			logger.log_error("UnifiedLogger", f"Failed to open UART ASSERV port {self.uart_port_asserv}: {e}")
			logger.log_warning("UnifiedLogger", "Continuing without UART ASSERV logging")
			self.serial_port_asserv = None

		# Open UART serial port AUTOM
		try:
			self.serial_port_autom = serial.Serial(
				port=self.uart_port_autom,
				baudrate=self.uart_baudrate,
				timeout=0.1  # Non-blocking with small timeout
			)
			logger.log_info("UnifiedLogger", f"Opened UART AUTOM on {self.uart_port_autom} @ {self.uart_baudrate} baud")
		except Exception as e:
			logger.log_error("UnifiedLogger", f"Failed to open UART AUTOM port {self.uart_port_autom}: {e}")
			logger.log_warning("UnifiedLogger", "Continuing without UART AUTOM logging")
			self.serial_port_autom = None

		# Create timestamped log file
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.log_filename = os.path.join(self.log_dir, f"unified_{timestamp}.txt")

		try:
			self.log_file = open(self.log_filename, "w", buffering=1)  # Line buffering
			logger.log_info("UnifiedLogger", f"Unified logging to: {self.log_filename}")

			# Write header to file with unified timestamp
			self.log_file.write("=" * 80 + "\n")
			self.log_file.write(f"Unified Debug Log (UART + CAN) - Started: {timestamp}\n")
			self.log_file.write(f"Program started at: {logger.start_date}\n")
			self.log_file.write(f"All timestamps use unified clock: absolute (relative)\n")
			self.log_file.write("=" * 80 + "\n\n")
			self.log_file.flush()

			self.enabled = True

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Failed to create log file: {e}")
			if self.serial_port:
				self.serial_port.close()
			return

		# Start the UART listener threads
		self.running = True

		# Thread ASSERV
		if self.serial_port_asserv:
			self.uart_thread_asserv = threading.Thread(target=self._uart_listener_thread_asserv, daemon=True)
			self.uart_thread_asserv.start()
			logger.log_info("UnifiedLogger", "UART ASSERV listener thread started")
		else:
			logger.log_info("UnifiedLogger", "UART ASSERV logging disabled (no serial port)")

		# Thread AUTOM
		if self.serial_port_autom:
			self.uart_thread_autom = threading.Thread(target=self._uart_listener_thread_autom, daemon=True)
			self.uart_thread_autom.start()
			logger.log_info("UnifiedLogger", "UART AUTOM listener thread started")
		else:
			logger.log_info("UnifiedLogger", "UART AUTOM logging disabled (no serial port)")


	def _uart_listener_thread_asserv(self):
		"""
		Private method that runs in the background thread for ASSERV UART.
		Continuously reads UART data and writes to log file with [UART_ASSERV] tag.
		"""
		logger.log_info("UnifiedLogger", "UART ASSERV listener thread running")

		try:
			while self.running:
				# Check if data is available
				if self.serial_port_asserv.in_waiting > 0:
					# Read all available data
					data = self.serial_port_asserv.read(self.serial_port_asserv.in_waiting)

					# Try to decode as UTF-8, fallback to raw string
					try:
						text = data.decode('utf-8', errors='ignore')
					except:
						text = str(data)

					# Write to log file with [UART_ASSERV] tag and unified timestamp
					self.log_uart(text, "ASSERV")

				else:
					# Small sleep to avoid busy-waiting
					time.sleep(0.01)

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error in UART ASSERV listener thread: {e}")

		logger.log_info("UnifiedLogger", "UART ASSERV listener thread stopped")


	def _uart_listener_thread_autom(self):
		"""
		Private method that runs in the background thread for AUTOM UART.
		Continuously reads UART data and writes to log file with [UART_AUTOM] tag.
		"""
		logger.log_info("UnifiedLogger", "UART AUTOM listener thread running")

		try:
			while self.running:
				# Check if data is available
				if self.serial_port_autom.in_waiting > 0:
					# Read all available data
					data = self.serial_port_autom.read(self.serial_port_autom.in_waiting)

					# Try to decode as UTF-8, fallback to raw string
					try:
						text = data.decode('utf-8', errors='ignore')
					except:
						text = str(data)

					# Write to log file with [UART_AUTOM] tag and unified timestamp
					self.log_uart(text, "AUTOM")

				else:
					# Small sleep to avoid busy-waiting
					time.sleep(0.01)

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error in UART AUTOM listener thread: {e}")

		logger.log_info("UnifiedLogger", "UART AUTOM listener thread stopped")


	def log_uart(self, data, tag):
		"""
		Log UART data to the unified file with [UART_ASSERV] or [UART_AUTOM] tag.
		Thread-safe method called from UART listener threads.

		:param data: UART data string to log
		:param tag: "ASSERV" or "AUTOM"
		"""
		if not self.enabled or self.log_file is None:
			return

		try:
			with self.lock:
				# Use unified timestamp for perfect synchronization with CAN logs
				timestamp = logger.get_unified_timestamp_absolute()

				# Format: [timestamp] [UART_ASSERV] {data} or [timestamp] [UART_AUTOM] {data}
				# Note: UART data already contains newlines from microcontroller
				log_line = f"[{timestamp}] [UART_{tag}] {data}"

				self.log_file.write(log_line)
				self.log_file.flush()

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error writing UART to log file: {e}")


	def log_can_tx(self, node_id, command_id, action_id, params):
		"""
		Log CAN TX message to the unified file with [CAN TX] tag.
		Thread-safe method called from CAN transmission code.

		:param node_id: CAN node ID
		:param command_id: Command ID (incremental counter for correlation with RX)
		:param action_id: Action command ID being sent
		:param params: List of 6 parameters being sent
		"""
		if not self.enabled or self.log_file is None:
			return

		try:
			with self.lock:
				# Use unified timestamp for perfect synchronization
				timestamp = logger.get_unified_timestamp_absolute()

				# Format: [timestamp] [CAN TX] Node X → cmd_id action_id params
				log_line = f"[{timestamp}] [CAN TX] Node {node_id} → cmd_id:{command_id} action:{action_id} params:{params}\n"

				self.log_file.write(log_line)
				self.log_file.flush()

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error writing CAN TX to log file: {e}")


	def log_can_rx(self, node_id, vals):
		"""
		Log CAN RX message to the unified file with [CAN RX] tag.
		Thread-safe method called from CAN message handlers.

		:param node_id: CAN node ID
		:param vals: Decoded TPDO values [status, cmd_id, action_id, completed_id, error]
		"""
		if not self.enabled or self.log_file is None:
			return

		try:
			with self.lock:
				# Use unified timestamp for perfect synchronization
				timestamp = logger.get_unified_timestamp_absolute()

				# Format: [timestamp] [CAN RX] Node X → status cmd_id action completed error
				log_line = f"[{timestamp}] [CAN RX] Node {node_id} → status:{vals[0]} cmd_id:{vals[1]} action:{vals[2]} completed:{vals[3]} error:{vals[4]}\n"

				self.log_file.write(log_line)
				self.log_file.flush()

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error writing CAN RX to log file: {e}")


	def log_python(self, tag, message):
		"""
		Log Python application messages to the unified file with [PYTHON] tag.
		Thread-safe method called from logger.py when application logs a message.

		:param tag: Tag/module name (e.g., "Main", "CanOpenWrapper")
		:param message: Log message content
		"""
		if not self.enabled or self.log_file is None:
			return

		try:
			with self.lock:
				# Use unified timestamp for perfect synchronization
				timestamp = logger.get_unified_timestamp_absolute()

				# ADDED BY CLAUDE: Python application logs with [PYTHON] tag
				# Format: [timestamp] [PYTHON] [tag] message
				log_line = f"[{timestamp}] [PYTHON] [{tag}] {message}\n"

				self.log_file.write(log_line)
				self.log_file.flush()

		except Exception as e:
			# Avoid infinite loop: don't use logger.log_error here
			print(f"[UnifiedLogger] Error writing Python log to file: {e}")


	def stop(self):
		"""
		Stop the unified logger and close all resources.
		Stops UART thread, closes serial port and log file.
		"""
		if not self.enabled:
			logger.log_warning("UnifiedLogger", "Unified logger not running")
			return

		logger.log_info("UnifiedLogger", "Stopping unified logger...")

		# Signal UART threads to stop
		self.running = False

		# Wait for UART ASSERV thread to finish (max 2 seconds)
		if self.uart_thread_asserv and self.uart_thread_asserv.is_alive():
			self.uart_thread_asserv.join(timeout=2.0)

		# Wait for UART AUTOM thread to finish (max 2 seconds)
		if self.uart_thread_autom and self.uart_thread_autom.is_alive():
			self.uart_thread_autom.join(timeout=2.0)

		# Close serial port ASSERV
		if self.serial_port_asserv and self.serial_port_asserv.is_open:
			self.serial_port_asserv.close()
			logger.log_info("UnifiedLogger", f"Closed UART ASSERV port {self.uart_port_asserv}")

		# Close serial port AUTOM
		if self.serial_port_autom and self.serial_port_autom.is_open:
			self.serial_port_autom.close()
			logger.log_info("UnifiedLogger", f"Closed UART AUTOM port {self.uart_port_autom}")

		# Close log file
		with self.lock:
			if self.log_file:
				# Write footer with unified timestamp
				timestamp = logger.get_unified_timestamp_absolute()
				self.log_file.write("\n" + "=" * 80 + "\n")
				self.log_file.write(f"Unified Debug Log - Stopped: {timestamp}\n")
				self.log_file.write("=" * 80 + "\n")

				self.log_file.close()
				logger.log_info("UnifiedLogger", f"Closed log file: {self.log_filename}")

		self.enabled = False
		logger.log_info("UnifiedLogger", "Unified logger stopped successfully")


	def is_enabled(self):
		"""
		Check if the unified logger is currently enabled.

		:return: True if enabled, False otherwise
		"""
		return self.enabled


# Global instance to be set from init_interface.py
unified_logger :UnifiedLogger  = None

'''
