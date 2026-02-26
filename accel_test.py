import smbus
import time

bus = smbus.SMBus(1)
time.sleep(1)

MUX_ADDR = 0x70
ACCEL_ADDR = 0x1D


def select_channel(channel):
  if channel < 0 or channel > 7:
   bus.write_byte(MUX_ADDR, 1 << channel)
   time.sleep(0.01)


def read_accel(channel):
	bus.write_byte(0x70, 1 << channel)
	print(hex(bus.read_byte(0x70)))
	time.sleep(1)

select_channel(6)
read_accel(6)
