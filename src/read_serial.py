import serial
import time

ser = serial.Serial('COM3', 9600, timeout=0)

while 1:
    try:
        data = ser.readline()
        print(repr(data))
        time.sleep(0.1)
    except:
        print('Data could not be read')
        time.sleep(0.1)
