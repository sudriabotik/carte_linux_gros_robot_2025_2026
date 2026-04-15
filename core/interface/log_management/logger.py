import sys

import time
import datetime

# Global timing reference for all loggers (UART, CAN, console)
initial_time = time.time()
start_date = datetime.datetime.now()
sys.stdout.write(f"[INFO] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [Logger] logger initialized\n")


def get_unified_timestamp_relative():
	"""
	Get unified relative timestamp (time since program start).
	Used for perfect synchronization between console, UART, and CAN logs.

	:return: Formatted string "t+X.XXXXXXs"
	"""
	elapsed = time.time() - initial_time
	return f"t+{elapsed:.6f}s"


def get_unified_timestamp_absolute():
	"""
	Get unified absolute timestamp with microsecond precision.
	Uses the same time reference as relative timestamp for perfect synchronization.

	:return: Formatted string "YYYY-MM-DD HH:MM:SS.mmm (t+X.XXXs)"
	"""
	elapsed = time.time() - initial_time
	current_time = datetime.datetime.now()
	timestamp_abs = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Milliseconds
	timestamp_rel = f"t+{elapsed:.6f}s"
	return f"{timestamp_abs} ({timestamp_rel})"

def log_verbose(source : str, message : str) :
	sys.stdout.write(f"[VERB] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [{source}] : {message}\n")

def log_info(source : str, message : str) :
	sys.stdout.write(f"[INFO] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [{source}] : {message}\n")

def log_warning(source : str, message : str) :
	sys.stdout.write(f"[WARN] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [{source}] : {message}\n")

def log_error(source : str, message : str) :
	sys.stderr.write(f"[ERR] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [{source}] : {message}\n")

def log_traceback(source : str, message : str) :
	sys.stderr.write(f"[TRCBCK] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [{source}] : {message}\n")
