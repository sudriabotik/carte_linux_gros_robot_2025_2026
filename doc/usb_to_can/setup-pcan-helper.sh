#!/usr/bin/bash

# Script helper pour udev - Configure can0 automatiquement
# Ce script est appelé par la règle udev 99-pcan-usb.rules
#
# Installation:
#   sudo cp setup-pcan-helper.sh /usr/local/bin/
#   sudo chmod +x /usr/local/bin/setup-pcan-helper.sh

# Attendre que l'interface soit prête
sleep 1

# Configurer can0
/sbin/ip link set can0 type can bitrate 500000
/sbin/ip link set can0 up

# Logger l'événement
logger "PCAN-USB: Interface can0 configurée automatiquement (500 kbps)"

exit 0
