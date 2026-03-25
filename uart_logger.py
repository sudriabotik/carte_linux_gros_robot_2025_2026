"""
UART Logger Module - Non-blocking UART data logger using threading

This module provides a threaded UART logger that runs in the background
without blocking the main program execution.
"""

import serial
import threading
import time
import os
import logger


class UartLogger:
	"""
	Non-blocking UART logger that runs in a separate thread.

	Reads data from UART port and writes it to a timestamped log file
	in the log/ directory.
	"""

	def __init__(self, port="/dev/ttyS2", baudrate=1000000, log_dir="log"):
		"""
		Initialize the UART logger.

		:param port: UART port device (default: /dev/ttyS2 for Rock5 pins 8/10)
		:param baudrate: UART baudrate (default: 1000000)
		:param log_dir: Directory to store log files (default: "log")
		"""
		self.port = port
		self.baudrate = baudrate
		self.log_dir = log_dir

		# Thread control
		self.running = False
		self.thread = None

		# Serial port and log file handles
		self.serial_port = None
		self.log_file = None
		self.log_filename = None

		# Create log directory if it doesn't exist
		if not os.path.exists(self.log_dir):
			os.makedirs(self.log_dir)
			logger.log_info("UartLogger", f"Created log directory: {self.log_dir}")


	def start(self):
		"""
		Start the UART logger thread.
		Opens the serial port and begins logging to a timestamped file.
		"""
		if self.running:
			logger.log_warning("UartLogger", "UART logger already running")
			return

		try:
			# Open serial port
			self.serial_port = serial.Serial(
				port=self.port,
				baudrate=self.baudrate,
				timeout=0.1  # Non-blocking with small timeout
			)
			logger.log_info("UartLogger", f"Opened UART on {self.port} @ {self.baudrate} baud")

		except Exception as e:
			logger.log_error("UartLogger", f"Failed to open UART port {self.port}: {e}")
			return

		# Create timestamped log file using unified timestamp from logger module
		import datetime
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.log_filename = os.path.join(self.log_dir, f"uart_{timestamp}.txt")

		try:
			self.log_file = open(self.log_filename, "w", buffering=1)  # Line buffering
			logger.log_info("UartLogger", f"Logging to: {self.log_filename}")
		except Exception as e:
			logger.log_error("UartLogger", f"Failed to create log file: {e}")
			self.serial_port.close()
			return

		# Start the listener thread
		self.running = True
		self.thread = threading.Thread(target=self._uart_listener_thread, daemon=True)
		self.thread.start()

		logger.log_info("UartLogger", "UART logger thread started")


	def _uart_listener_thread(self):
		"""
		Private method that runs in the background thread.
		Continuously reads UART data and writes to log file.
		"""
		logger.log_info("UartLogger", "UART listener thread running")

		try:
			while self.running:
				# Check if data is available
				if self.serial_port.in_waiting > 0:
					# Read all available data
					data = self.serial_port.read(self.serial_port.in_waiting)

					# Try to decode as UTF-8, fallback to raw string
					try:
						text = data.decode('utf-8', errors='ignore')
					except:
						text = str(data)

					# Write to log file
					self.log_file.write(text)
					self.log_file.flush()  # Ensure data is written immediately

				else:
					# Small sleep to avoid busy-waiting
					time.sleep(0.01)

		except Exception as e:
			logger.log_error("UartLogger", f"Error in UART listener thread: {e}")

		logger.log_info("UartLogger", "UART listener thread stopped")


	def stop(self):
		"""
		Stop the UART logger thread and close resources.
		Waits for the thread to finish and closes serial port and log file.
		"""
		if not self.running:
			logger.log_warning("UartLogger", "UART logger not running")
			return

		logger.log_info("UartLogger", "Stopping UART logger...")

		# Signal thread to stop
		self.running = False

		# Wait for thread to finish (max 2 seconds)
		if self.thread and self.thread.is_alive():
			self.thread.join(timeout=2.0)

		# Close serial port
		if self.serial_port and self.serial_port.is_open:
			self.serial_port.close()
			logger.log_info("UartLogger", f"Closed UART port {self.port}")

		# Close log file
		if self.log_file:
			self.log_file.close()
			logger.log_info("UartLogger", f"Closed log file: {self.log_filename}")

		logger.log_info("UartLogger", "UART logger stopped successfully")


	def is_running(self):
		"""
		Check if the UART logger is currently running.

		:return: True if running, False otherwise
		"""
		return self.running
