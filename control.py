import serial
import numpy as np
import cv2


def send_commends(ser, motors, commands):
    for motor in motors:
        for direction_cmd in commands:
            command_string = bytes(2)
            command_string = bytearray(command_string)
            command_string[0] = motor  # 2 motor 1, 4 motor 2, 8 motor 3
            command_string[1] = direction_cmd  # 2 forward, 4 backward, 8 release
            print(command_string)
            command_string = bytes(command_string)
            ser.write(command_string)  # write a string


def test_dc_motors():
    motors = set()
    commands = []
    # ser = serial.Serial('COM5')  # open serial port
    ser = serial.Serial('/dev/ttyUSB1')  # open serial port
    print(ser.name)  # check which port was really used

    while True:
        img = np.zeros((200, 200), np.uint8)
        cv2.imshow('Main', img)
        key = cv2.waitKey(2)
        if key > 0:
            key = chr(key)

        if key in [ord('q')]:
            break
        if key in ['2', '4', '8']:
            motor = int(key)
            if motor in motors:
                motors.remove(motor)
            else:
                motors.add(motor)
        if key == 'w':
            commands = [2]
        if key == 's':
            commands = [8]
        if key == 'x':
            commands = [4]

        print(key, list(motors), commands)
        send_commends(ser, motors, commands)

    ser.close()


test_dc_motors()
