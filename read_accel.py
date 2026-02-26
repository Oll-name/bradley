import serial

ser = serial.Serial('/dev/ttyUSB0' , 115200, timeout=1)

while True:
	line = ser.readline().decode('utf-8').strip()
	if not line:
		continue
		print("Nothing to read")
		ser.close()

	try:
		ax,ay,az = map(int,line.split('.'))
		print(ax,ay,az)
	except ValueError:
		pass
