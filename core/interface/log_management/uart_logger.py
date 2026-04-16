import sys
import os

import serial
import threading
import time

import core.interface.log_management.logger as logger


UART_AUTOM = "/dev/ttyS6"
UART_ASSERV = "/dev/ttyS2"



class UartLogger :


	def __init__(self, uart_port : str = "/dev/ttyS2", uart_baudrate : int = 1000000) :

		self.uart_port : str = uart_port
		self.uart_baudrate : int = uart_baudrate

		self.serial_port : serial.Serial = serial.Serial(
			port=self.uart_port,
			baudrate=self.uart_baudrate,
			timeout=0.1  # Non-blocking with small timeout
		)

		self.running : bool = True

		self.uart_thread : threading.Thread = threading.Thread(target=self._uart_listener_thread, daemon=True)
		self.uart_thread.start()

	

	def destroy(self) :
		self.running = False
		self.serial_port.close()

	

	def _uart_listener_thread(self):
		"""
		Private method that runs in the background thread.
		Continuously reads UART data and writes to log file with [UART] tag.
		"""
		logger.log_info("UnifiedLogger", "UART listener thread running")

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

					# Write to log file with [UART] tag and unified timestamp
					logger.log_info("UART", text)

				else:
					# Small sleep to avoid busy-waiting
					time.sleep(0.01)

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error in UART listener thread: {e}")

		logger.log_info("UnifiedLogger", "UART listener thread stopped")



_uart_logger : UartLogger



try :
	uart_logger = UartLogger(UART_ASSERV, 1000000)
except Exception as e :
	logger.log_error("UartLogger", "Cannot start : {e}")



def close() :
	try :
		_uart_logger.destroy()
	except Exception as e :
		logger.log_error("UartLogger", "Cannot stop : {e}")

