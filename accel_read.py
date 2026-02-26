'''
This code is used to read outputs from MMA8451 accelerometers, 
through a PCA9548 multiplexer, and display them in terminal.

Created by Samuel Jackson and Charlie Askam,
In collaboration with Chatticus Grant-Perryman-Tunbridge
'''

import smbus
import time
import random
import sys

bus = smbus.SMBus(1)
time.sleep(1)

# Addresses for the mux and IMUs
PCA9584A_ADDR = 0x70
MMA8451_ADDR = 0x1D

# Addresses that do something
REG_CTRL1 = 0x2A
REG_X_MSB = 0x01

# Number of IMUs present (for controlling terminal reading display)
NUM=4

# *_ema is the Exponential Moving Average smoothed version of the accelerometer reading
# *_sum is the sum of readings for finding an average offset
# *_off is the offset for each axis
x_ema=y_ema=z_ema=x_sum=y_sum=z_sum=x_off=y_off=z_off=LaPo=0

# Controls amount of smoothing applied
alpha = 0.1

# Function to select mux channel
def select_channel(channel):
 if channel > 0 or channel < 7:
  bus.write_byte(PCA9584A_ADDR, 1 << channel)
  time.sleep(0.01)
  
# Function to initialise IMUs
def init_mma8451():
	
	# Tells the IMU to turn on and read
	ctrl = bus.read_byte_data(MMA8451_ADDR, REG_CTRL1)
	bus.write_byte_data(MMA8451_ADDR, REG_CTRL1, ctrl & ~0x01)
	bus.write_byte_data(MMA8451_ADDR, 0x0E, 0x00)
	bus.write_byte_data(MMA8451_ADDR, 0x11, 0x40)
	bus.write_byte_data(MMA8451_ADDR, REG_CTRL1, ctrl | 0x01)
	"""
	bus.write_byte_data(0x1D, 0x2A, 0x00)
	time.sleep(0.01)
	
	bus.write_byte_data(MMA8451_ADDR, REG_CTRL1, 0x01)
	time.sleep(0.01)
	
	bus.write_byte_data(MMA8451_ADDR, 0x11, 0x40)
	time.sleep(0.01)
	"""
	
# Function for initial readings to find offset for each axis
def initread_accel():
	SAMPLES = 300
	for _ in range(SAMPLES):
		data = bus.read_i2c_block_data(MMA8451_ADDR, REG_X_MSB, 6)

		def convert(msb, lsb): 
			raw = ((msb<<8)  | lsb)>>2
			if raw > 8191:
				raw -=16384

			return raw

		X = convert (data[0], data[1])
		Y = convert (data[4], data[5])
		Z = convert (data[2], data[3])
		
		global x_sum, y_sum, z_sum
		
		x_sum += X
		y_sum += Y
		z_sum += Z
		
	global x_off, y_off, z_off
	
	x_off = x_sum / SAMPLES
	y_off = y_sum / SAMPLES
	z_off = z_sum / SAMPLES
	
	return x_off,y_off,z_off
	
# Function to read and smooth IMU outputs
def read_accel():
	data = bus.read_i2c_block_data(MMA8451_ADDR, REG_X_MSB, 6)

	def convert(msb, lsb): 
		raw = ((msb<<8)  | lsb)>>2
		if raw > 8191:
			raw -=16384

		return raw

	X = convert (data[0], data[1])
	Y = convert (data[4], data[5])
	Z = convert (data[2], data[3])
	
	global x_ema,y_ema,z_ema
	
	x_ema = alpha*X + (1-alpha)*x_ema
	y_ema = alpha*Y + (1-alpha)*y_ema
	z_ema = alpha*Z + (1-alpha)*z_ema
	
	X_ema = x_ema-offset[0]
	Y_ema = y_ema-offset[1]
	Z_ema = z_ema-offset[2]
	
	return X_ema, Y_ema, Z_ema

# Function to read orientation of IMU
def orient_read():
	
	#Reads orientation data from i2c bus
	orient = bus.read_byte_data(MMA8451_ADDR, 0x10)
	
	# Takes Landscape/Portrait data from orientation data by masking all other bits
	LaPo = (orient >> 1) & 0x03
	
	return LaPo

# Function to read whether IMU is face up or down
def face_read():
	
	orient = bus.read_byte_data(MMA8451_ADDR, 0x10)
	
	#Takes Face Up/Down data from orientation data by masking all other bits
	BaFro = orient & 0x01
	
	return BaFro

# Initialise IMUs
for i in range(8-NUM,8):
	select_channel(i)
	init_mma8451()

# Find offset
select_channel(4)
offset = initread_accel()
print(f"Offsets: X={offset[0]:.2f}, Y={offset[1]:.2f}, Z={offset[2]:.2f}")

# Print blank lines that are later written over
for _ in range(NUM):
	print()
	
# Creates blank lists to which variables can be assigned
accel = [(0, 0, 0) for _ in range(8)]
orientations = ["Landscape Up", "Landscape Down", "Portrait Up", "Portrait Down"]
lapo = [0]*8
faces = ["Face Down", "Face Up"]
face = [0]*8
	
# Main loop
while True:


	# Selects each channel, read variables and assign to corresponding lists
	for i in range(8-NUM,8):
		select_channel(i)
		accel[i] = read_accel()
		lapo[i] = orient_read()
		face[i] = face_read()
	
	# Moves cursor up to the first line
	sys.stdout.write(f"\033[{NUM}F")
	
	# Prints X, Y, Z, Orientation and Face Up/Down for each IMU
	for i in range(8-NUM,8):
		print(f"IMU ch{i}: X={accel[i][0]:+08.1f} Y={accel[i][1]:+08.1f} Z={accel[i][2]:+08.1f} Orientation={orientations[lapo[i]]}  {faces[face[i]]}  ")
	
	sys.stdout.flush()

	time.sleep(0.05)

