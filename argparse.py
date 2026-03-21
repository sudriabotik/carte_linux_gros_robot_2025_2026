"""
Parse the parameters provided in key:val format with space separation and put them in a dictionary.
Is checks if all given parameters already exists, and also has a dictionary with all paramters and their default value.
"""

import logger

ARG_OPTION_STRAT = str("strat")

ARG_TABLE = {
	ARG_OPTION_STRAT : (str, "./strats/strat_demo.py")
}

def parse(args : list[str]) :
	"""Makes a dictionary from the passed argument list"""

	key_val_separator : str = ":"

	options = {}

	for arg in args :

		split = arg.split(key_val_separator)

		if len(split) != 2 :
			logger.log_error("ArgParse", f"the argument {arg} couldn't be split correctly")
		
		if not split[0] in ARG_TABLE :
			logger.log_error("ArgParse", f"the argument {arg} does not exist")
		
		if ARG_TABLE[split[0]][0] == str : options[split[0]][1] = str(split[1])
		elif ARG_TABLE[split[0]][0] == float : options[split[0]][1] = float(split[1])
	
	return options

def get_option(key : str) :
	"""Checks if the option has been given in the program call, otherwise returns a default value"""

