import sys

import time
import datetime

initial_time = time.time()
start_date = datetime.datetime.now()
sys.stdout.write(f"[INFO] [run_started:{start_date}] [t+{time.time() - initial_time:.6f}s] [Logger] logger initialized\n")

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
