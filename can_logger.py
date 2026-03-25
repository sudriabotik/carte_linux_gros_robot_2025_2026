"""
CAN Logger Module - Logs CAN messages to timestamped files

This module provides a file logger for CAN messages that writes to timestamped
log files in the log_can/ directory.
"""

import os
import threading
import datetime
import logger


class CanLogger:
	"""
	File logger for CAN messages.

	Writes CAN message logs to timestamped files in log_can/ directory.
	Thread-safe for concurrent access from CAN message handlers.
	"""

	def __init__(self, log_dir="log_can"):
		"""
		Initialize the CAN logger.

		:param log_dir: Directory to store CAN log files (default: "log_can")
		"""
		self.log_dir = log_dir
		self.log_file = None
		self.log_filename = None
		self.lock = threading.Lock()  # Thread-safe file writing
		self.enabled = False

		# Create log directory if it doesn't exist
		if not os.path.exists(self.log_dir):
			os.makedirs(self.log_dir)
			logger.log_info("CanLogger", f"Created log directory: {self.log_dir}")


	def start(self):
		"""
		Start the CAN logger.
		Creates a timestamped log file and enables logging.
		"""
		if self.enabled:
			logger.log_warning("CanLogger", "CAN logger already started")
			return

		# Create timestamped log file
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.log_filename = os.path.join(self.log_dir, f"can_{timestamp}.txt")

		try:
			self.log_file = open(self.log_filename, "w", buffering=1)  # Line buffering
			logger.log_info("CanLogger", f"CAN logging to: {self.log_filename}")
			self.enabled = True

			# Write header to file with unified timestamp
			self.log_file.write("=" * 80 + "\n")
			self.log_file.write(f"CAN Debug Log - Started: {timestamp}\n")
			self.log_file.write(f"Program started at: {logger.start_date}\n")
			self.log_file.write(f"All timestamps use unified clock: absolute (relative)\n")
			self.log_file.write("=" * 80 + "\n\n")
			self.log_file.flush()

		except Exception as e:
			logger.log_error("CanLogger", f"Failed to create CAN log file: {e}")
			self.enabled = False


	def log_message(self, node_id, vals):
		"""
		Log a CAN message to the file.
		Thread-safe method called from CAN message handlers.

		:param node_id: CAN node ID
		:param vals: Decoded TPDO values [status, cmd_id, action_id, completed_id, error]
		"""
		if not self.enabled or self.log_file is None:
			return

		try:
			with self.lock:
				# Use unified timestamp for perfect synchronization with UART and console logs
				timestamp = logger.get_unified_timestamp_absolute()

				# Format: unified_timestamp | Node ID | status | cmd_id | action | completed | error
				log_line = f"[{timestamp}] Node {node_id} → status:{vals[0]} cmd_id:{vals[1]} action:{vals[2]} completed:{vals[3]} error:{vals[4]}\n"

				self.log_file.write(log_line)
				self.log_file.flush()

		except Exception as e:
			logger.log_error("CanLogger", f"Error writing to CAN log file: {e}")


	def stop(self):
		"""
		Stop the CAN logger and close the log file.
		"""
		if not self.enabled:
			logger.log_warning("CanLogger", "CAN logger not running")
			return

		logger.log_info("CanLogger", "Stopping CAN logger...")

		with self.lock:
			if self.log_file:
				# Write footer with unified timestamp
				timestamp = logger.get_unified_timestamp_absolute()
				self.log_file.write("\n" + "=" * 80 + "\n")
				self.log_file.write(f"CAN Debug Log - Stopped: {timestamp}\n")
				self.log_file.write("=" * 80 + "\n")

				self.log_file.close()
				logger.log_info("CanLogger", f"Closed CAN log file: {self.log_filename}")

			self.enabled = False


	def is_enabled(self):
		"""
		Check if the CAN logger is currently enabled.

		:return: True if enabled, False otherwise
		"""
		return self.enabled
