import sys

import time
import datetime

start_date = datetime.datetime.now()
sys.stdout.write(f"[INFO] [run_started:{start_date}] [t+{time.time()}s] [LOGGER] logger initialized")

def log_info(source : str, message : str) :
	sys.stdout.write(f"[INFO] [run_started:{start_date}] [t+{time.time()}s] [{source.upper()}] : {message}\n")

def log_warning(source : str, message : str) :
	sys.stdout.write(f"[WARN] [run_started:{start_date}] [t+{time.time()}s] [{source.upper()}] : {message}\n")

def log_error(source : str, message : str) :
	sys.stderr.write(f"[ERR] [run_started:{start_date}] [t+{time.time()}s] [{source.upper()}] : {message}\n")
