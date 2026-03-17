#!/bin/bash

if [[ $# -lt 1 ]]
then
	echo -e "usage :\n${0} <serialfile>\n for example : ${0} /dev/ttyACM0"
	exit 1
fi

# assumes 500 000 baudrate
sudo slcand -f -o -c -s6 "${1}" can0
sudo ip link set up can0