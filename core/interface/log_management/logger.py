from io import TextIOWrapper
import sys
import os

import time
import datetime
import threading
from tracemalloc import start

from can.io import logger


# configuration variables
use_file = True # write to file
use_std = True # write to stdout and sterr

# constants
#LOG_DIR = "log"

# Chemin absolu basé sur le répertoire de travail (où main.py se trouve)
# main.py est toujours la racine du projet, donc on utilise getcwd()
LOG_DIR = os.path.join(os.getcwd(), "log")

# Global timing reference for all loggers (UART, CAN, console)
initial_time = -1
start_date = datetime.datetime.now()




def get_timestamp_relative():
	"""
	Get unified relative timestamp (time since program start).
	Used for perfect synchronization between console, UART, and CAN logs.

	:return: Formatted string "t+X.XXXXXXs"
	"""
	elapsed = 0
	if initial_time != -1 :
		elapsed = time.time() - initial_time
	return f"t+{elapsed:.6f}s"


def get_timestamp_absolute():
	"""
	Get unified absolute timestamp with millisecond precision.
	Uses the same time reference as relative timestamp for perfect synchronization.

	:return: Formatted string "YYYY-MM-DD HH:MM:SS.mmm"
	"""
	current_time = datetime.datetime.now()
	timestamp_abs = current_time.strftime("%Y-%m-%d_%H:%M:%S:%f")[:-3]  # Milliseconds
	return f"{timestamp_abs}"



class Logger :

	def __init__(self) -> None:

		if not os.path.exists(LOG_DIR):
			os.makedirs(LOG_DIR)

		self.start_date : str = get_timestamp_absolute()
		
		# Log de diagnostic pour vérifier le chemin absolu des logs
		print(f"[LOGGER] LOG_DIR absolu utilisé: {LOG_DIR}", file=sys.stderr, flush=True)

		self.current_log_dir : str = os.path.join(LOG_DIR, self.start_date)
		if not os.path.exists(self.current_log_dir) :
			os.makedirs(self.current_log_dir)

		# threads native ids as keys
		self.logfiles : dict[int, TextIOWrapper] = {}

		self.lock : threading.Lock = threading.Lock()

		self.write(f">> [INFO] [t+{time.time() - initial_time:.6f}s] [Logger] logger initialized\n")
	
	def __del__(self) -> None :
		with self.lock :
			for logfile in self.logfiles.values() :
				logfile.flush()
				logfile.close()
	
	# use the threading id and program start time to fetch/create a logfile in a folder
	def get_or_make_logfile_for_thread(self) -> TextIOWrapper :
		with self.lock :
			if threading.get_native_id() in self.logfiles.keys() :
				return self.logfiles[threading.get_native_id()]
			else :
				self.logfiles[threading.get_native_id()] = open(os.path.join(self.current_log_dir, f"log_{threading.get_native_id()}.txt"), "w", buffering=1)
				return self.logfiles[threading.get_native_id()]

	
	"""
	Will log the given line finished by a line break to the correct outputs.
	"""
	def write(self, line : str) :

		logfile = self.get_or_make_logfile_for_thread()

		with self.lock :
			if use_std :
				sys.stdout.write(line + "\n")
			if use_file :
				logfile.write(line + "\n")
				logfile.flush()

	"""
	Will log the given line finished by a line break to the correct outputs.
	"""
	""" 
	def write_err(self, line : str, suffix : str = "log") :

		logfile = self.get_or_make_logfile_for_thread(suffix)

		with self.lock :
			if use_std :
				sys.stdout.write(line + "\n")
			if use_file :
				logfile.write(line + "\n")
				logfile.flush()
	"""

global instance
instance : Logger | None = None
try :
	instance = Logger()
except Exception as e :
	sys.stderr.write(f">> [FATAL] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [LOGGER] cannot start logger : {e}\n")


def _format_msg(category : str, source : str, message : str) :
	return f">> [{category}] [{get_timestamp_absolute()}] [{get_timestamp_relative()}] [{source}] : {message}\n"

def log_verbose(source : str, message : str) :
	if (instance == None) : return
	instance.write(_format_msg("VERB", source, message))

def log_can_tx(source : str, message : str) :
	if (instance == None) : return
	instance.write(_format_msg("CAN_TX", source, message))

def log_info(source : str, message : str) :
	if (instance == None) : return
	instance.write(_format_msg("INFO", source, message))

def log_warning(source : str, message : str) :
	if (instance == None) : return
	instance.write(_format_msg("WARN", source, message))

def log_error(source : str, message : str) :
	if (instance == None) : return
	#instance.write_err(_format_msg("ERR", source, message))
	instance.write(_format_msg("ERR", source, message))

def log_traceback(source : str, message : str) :
	if (instance == None) : return
	#instance.write_err(_format_msg("TRCBCK", source, message))
	instance.write(_format_msg("ERR", source, message))


"""
the relative timestamps stays zero until this function is called. Then, it starts counting up.
"""
def set_time_origin() :
	global initial_time
	initial_time = time.time()


def close() :
	global instance
	del instance
