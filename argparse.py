import sys

import logger

ARG_TABLE = {
	"strat" : ("str", "./strats/strat_demo.py")
}

def parse(args : list[str]) :
	"""Makes a dictionary from the passed argument list"""

	key_val_separator : str = "="

	options = {}

	for arg in args :

		split = arg.split(key_val_separator)

		if len(split) != 2 :
			logger.log_error("argparse", f"the argument {arg} couldn't be split correctly")
		
		if not split[0] in ARG_TABLE :
			logger.log_error("argparse", f"the argument {arg} does not exist")
		
		
		options[split[0]] = split[1]
	
	return options

def get_option(key : str) :
	"""Checks if the option has been given in the program call, otherwise returns a default value"""

