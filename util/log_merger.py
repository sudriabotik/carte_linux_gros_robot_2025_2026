from io import TextIOWrapper
import os
import sys

import re



def usage() :
	print("python log_merger.py <log_date>")


def get_absolute_time_from_logline(line : str) :
	match = re.match(">> [.*] [(.*)].*\n", line)
	if match :
		return match.group(0)
	else :
		return None

def get_oldest_line(lines : list[str]) :
	oldest_val = "9999:99:99_99:99:99:999"
	oldest_index = -1

	for i in range(len(lines)) :
		time = get_absolute_time_from_logline(lines[i])
		if time != None :
			if time < oldest_val :
				oldest_index = i
	return oldest_index

def unify(log_dir : str, log_date : str) :

	current_log_dir = os.path.join(log_dir, log_date)

	print(f"attempting to unify {current_log_dir}")

	if not os.path.exists(current_log_dir) :
		sys.stderr.write(f"error : no path found for {current_log_dir}\n")
		return



	files : list[TextIOWrapper] = []
	files_currentlines : list[str] = []
	for file in os.listdir(current_log_dir) :
		file = open(os.path.join(current_log_dir, file))
		files.append(file)
		files_currentlines.append(file.readline())
	
	
	with open(os.path.join(current_log_dir, "unified_log.txt"), "w") as out :
	
		while any(files_currentlines) :

			i = get_oldest_line(files_currentlines)

			# append the oldest line to the main file and get the next line for the file it was taken from
			if i != -1 :
				out.write(files_currentlines[i] + "\n")
				files_currentlines[i] = files[i].readline()
		


 
if __name__ == "__main__":
    
	if sys.argv != 1 :
		usage()
	
	unify("log", sys.argv[0])
