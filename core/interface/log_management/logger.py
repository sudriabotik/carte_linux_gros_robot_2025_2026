from io import TextIOWrapper
import sys
import os

import time
import datetime
import threading

from can.io import logger


# configuration variables
use_file = True # write to file
use_std = True # write to stdout and sterr

# constants
LOG_DIR = "log"

# Global timing reference for all loggers (UART, CAN, console)
initial_time = time.time()
start_date = datetime.datetime.now()




def get_timestamp_relative():
	"""
	Get unified relative timestamp (time since program start).
	Used for perfect synchronization between console, UART, and CAN logs.

	:return: Formatted string "t+X.XXXXXXs"
	"""
	elapsed = time.time() - initial_time
	return f"t+{elapsed:.6f}s"


def get_timestamp_absolute():
	"""
	Get unified absolute timestamp with millisecond precision.
	Uses the same time reference as relative timestamp for perfect synchronization.

	:return: Formatted string "YYYY-MM-DD HH:MM:SS.mmm"
	"""
	current_time = datetime.datetime.now()
	timestamp_abs = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Milliseconds
	return f"{timestamp_abs}"



class Logger :

	def __init__(self) -> None:

		if not os.path.exists(LOG_DIR):
			os.makedirs(LOG_DIR)

		self.log_filename : str = os.path.join(LOG_DIR, f"log_{get_timestamp_absolute()}.txt")
		# logfile directory as keys
		self.logfiles : dict[str, TextIOWrapper] = {}
		self.log_file : TextIOWrapper = open(self.log_filename, "w", buffering=1)  # Line buffering

		self.lock : threading.Lock = threading.Lock()

		self.write(f">> [INFO] [t+{time.time() - initial_time:.6f}s] [Logger] logger initialized\n")
	
	def __del__(self) -> None :
		self.log_file.flush()
		self.log_file.close()
	
	def get_or_make_logfile(self, dir : str) -> TextIOWrapper :
		with self.lock :
			if dir in self.logfiles.keys() :
				return self.logfiles[dir]
			else :
				self.logfiles[dir] = open(dir + "/" + self.log_filename, "w", buffering=1)
				return self.logfiles[dir]

	
	"""
	Will log the given line finished by a line break to the correct outputs.
	"""
	def write(self, line : str, directory : str = "log") :

		logfile = self.get_or_make_logfile(directory)

		with self.lock :
			if use_std :
				sys.stdout.write(line + "\n")
			if use_file :
				logfile.write(line + "\n")
				logfile.flush()

	"""
	Will log the given line finished by a line break to the correct outputs.
	"""
	def write_err(self, line : str, directory : str = "log") :

		logfile = self.get_or_make_logfile(directory)

		with self.lock :
			if use_std :
				sys.stdout.write(line + "\n")
			if use_file :
				logfile.write(line + "\n")
				logfile.flush()
			

global instance
instance : Logger | None = None
try :
	instance = Logger()
except Exception as e :
	sys.stderr.write(f">> [FATAL] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [LOGGER] cannot start logger : {e}\n")



def log_verbose(source : str, message : str, directory : str = "log") :
	if (instance == None) : return
	instance.write(f">> [VERB] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [{source}] : {message}\n", directory)

def log_info(source : str, message : str, directory : str = "log") :
	if (instance == None) : return
	instance.write(f">> [INFO] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [{source}] : {message}\n", directory)

def log_warning(source : str, message : str, directory : str = "log") :
	if (instance == None) : return
	instance.write(f">> [WARN] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [{source}] : {message}\n", directory)

def log_error(source : str, message : str, directory : str = "log") :
	if (instance == None) : return
	instance.write_err(f">> [ERR] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [{source}] : {message}\n", directory)

def log_traceback(source : str, message : str, directory : str = "log") :
	if (instance == None) : return
	instance.write_err(f">> [TRCBCK] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [{source}] : {message}\n", directory)


def close() :
	global instance
	del instance
