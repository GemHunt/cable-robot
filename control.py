import serial
import time
ser = serial.Serial('COM5')  # open serial port
print(ser.name)         # check which port was really used
for x in range(1):

    command_string = bytes(2)
    command_string = bytearray(command_string)
    command_string[0] = 8 #2 motor 1, 4 motor 2, 8 motor 3
    command_string[1] = 4 #2 forward, 4 backward, 8 release
    print(command_string)
    command_string = bytes(command_string)
    ser.write(command_string)     # write a string
    time.sleep(.1)
    print(ser.read_all())  # write a string
    time.sleep(.1)

ser.close()