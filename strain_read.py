import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)

print ("Reading strain gauge data..."/n)

while True:

 if ser.in_waiting > 0:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    print(line)
