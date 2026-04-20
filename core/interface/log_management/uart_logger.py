import sys
import os

import serial
import threading
import time

import core.interface.log_management.logger as logger


UART_AUTOM = "/dev/ttyS6"
UART_ASSERV = "/dev/ttyS2"



class UartLogger :


	def __init__(self, name : str, log_suffix : str, uart_port : str = "/dev/ttyS2", uart_baudrate : int = 1000000) :

		self.name : str = name
		self.uart_port : str = uart_port
		self.uart_baudrate : int = uart_baudrate
		self.log_suffix : str = log_suffix

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
		logger.log_info(self.name, f"UART listener thread running : {self.serial_port}", suffix=self.log_suffix)

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
					logger.log_info(self.name, text, suffix=self.log_suffix)

				else:
					# Small sleep to avoid busy-waiting
					time.sleep(0.01)

		except Exception as e:
			logger.log_error("UnifiedLogger", f"Error in UART listener thread: {e}")

		logger.log_info("UnifiedLogger", "UART listener thread stopped")




global _uart_asserv
_uart_asserv : UartLogger | None = None

global _uart_autom
_uart_autom : UartLogger | None = None


try :
	_uart_asserv = UartLogger("UART_ASSERV", "uart_asserv", UART_ASSERV, 1000000)
except Exception as e :
	logger.log_error("UartLogger", "Cannot start asserv listener : {e}")

try :
	_uart_autom = UartLogger("UART_AUTOM", "uart_autom", UART_AUTOM, 1000000)
except Exception as e :
	logger.log_error("UartLogger", "Cannot start autom listener : {e}")



def close() :
	try :
		if _uart_asserv != None :
			_uart_asserv.destroy()
		if _uart_autom != None :
			_uart_autom.destroy()
	except Exception as e :
		logger.log_error("UartLogger", "Cannot stop : {e}")

