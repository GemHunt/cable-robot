import serial
import time


def send_commends(ser,commands):
    for motor_cmd, direction_cmd in commands:
        command_string = bytes(2)
        command_string = bytearray(command_string)
        command_string[0] = motor_cmd  # 2 motor 1, 4 motor 2, 8 motor 3
        command_string[1] = direction_cmd  # 2 forward, 4 backward, 8 release
        print(command_string)
        command_string = bytes(command_string)
        ser.write(command_string)  # write a string


ser = serial.Serial('COM5')  # open serial port
print(ser.name)         # check which port was really used

for x in range(5):
    commands = [[2,2],[4,2],[8,2]]
    send_commends(ser,commands)
    time.sleep(1)
    commands = [[2, 8], [4, 8], [8, 8]]
    send_commends(ser, commands)
    time.sleep(.3)

    commands = [[2,4],[4,4],[8,4]]
    send_commends(ser,commands)
    time.sleep(1)
    commands = [[2, 8], [4, 8], [8, 8]]
    send_commends(ser, commands)
    time.sleep(.3)




ser.close()