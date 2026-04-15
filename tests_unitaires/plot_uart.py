
"""
Simple script to plot motor control curves from STM32 UART data
Replaces gnuplot with matplotlib
"""

import matplotlib.pyplot as plt
import sys

# Get filename from command line or use default
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "test_hold_paul_2.txt"

# Read the data
elapsed_time = []
distance_travelled = []
rotation_error = []
motor_command_position = []
motor_command_rotation = []
motor_r_rps = []
motor_l_rps = []

print(f"Reading data from {filename}...")

with open(filename, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        parts = line.split()
        if len(parts) >= 7:
            elapsed_time.append(float(parts[0]))
            distance_travelled.append(float(parts[1]))
            rotation_error.append(float(parts[2]))
            motor_command_position.append(float(parts[3]))
            motor_command_rotation.append(float(parts[4]))
            motor_r_rps.append(float(parts[5]))
            motor_l_rps.append(float(parts[6]))

print(f"Loaded {len(elapsed_time)} data points")

# Create the plot
plt.figure(figsize=(14, 8))

plt.plot(elapsed_time, distance_travelled, label='distance_travelled', linewidth=1)
plt.plot(elapsed_time, rotation_error, label='rotation_error', linewidth=1)
plt.plot(elapsed_time, motor_command_position, label='motor_command_position', linewidth=1)
plt.plot(elapsed_time, motor_command_rotation, label='motor_command_rotation', linewidth=1)
plt.plot(elapsed_time, motor_r_rps, label='motor_r_rps', linewidth=1)
plt.plot(elapsed_time, motor_l_rps, label='motor_l_rps', linewidth=1)

plt.xlabel('Elapsed Time (s)')
plt.ylabel('Values')
plt.title('UART Debug - Motor Control')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()

print("Displaying plot... (close window to exit)")
plt.show()
