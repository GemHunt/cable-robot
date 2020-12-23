import serial
import time
import numpy as np


def send_command(ser, motor, steps_in):
    command_string = bytes(4)
    command_string = bytearray(command_string)

    # Oh this is so bad! It's a int24...
    if steps_in < 0:
        command_string[0] = motor + 16
        steps = steps_in * -1
    else:
        steps = steps_in
        command_string[0] = motor

    int1 = steps % 256
    int256 = int((steps % 65536) / 256)
    int65536 = int(steps / 65536)

    # back2steps = (int65536 * 65536 + int256 * 256 + int1) * sign
    # print(steps_in, back2steps, int65536, int256, int1)

    print(steps_in, int65536, int256, int1)

    command_string[1] = int1
    command_string[2] = int256
    command_string[3] = int65536
    print(command_string)
    command_string = bytes(command_string)
    ser.write(command_string)  # write a string


def send_commands(ser, commands):
    send_command(ser, 2, int(commands[0]))
    time.sleep(.1)
    send_command(ser, 4, int(commands[1]))
    time.sleep(.1)
    send_command(ser, 8, int(commands[2]))


def test_steppers():
    ser = serial.Serial('COM5')  # open serial port
    print(ser.name)  # check which port was really used
    steps_start = np.array([1100, 1100, 1100])
    steps_end = np.array([4950, -3760, -4000])
    steps_diff = steps_start - steps_end
    # steps_end = steps_end - steps_diff * 5
    print(steps_diff)

    # send_commands([-2100, -8450, -8650])
    # send_commands([-7050, -4690, -4790])

    # steps_start * .5 + steps_end + .5
    #
    send_commands(ser, steps_start)
    #
    #

    print(steps_end)

    # move_steps = 1000
    #
    # #send_commend(ser,2,int(steps_start + move_steps * -.5))
    # #sys.exit()
    # send_commend(ser,2,int(steps_start + move_steps * -.7))
    # time.sleep(.1)
    # send_commend(ser,4,int(steps_start + move_steps * 1))
    # time.sleep(.1)
    # send_commend(ser,8,int(steps_start+ move_steps * 1))

    #
    # while True:
    #     img = np.zeros((200,200),np.uint8)
    #     cv2.imshow('Main', img)
    #     key = cv2.waitKey(2)
    #     if key > 0:
    #         key = chr(key)
    #
    #     if key in [ord('q')]:
    #         break
    #     if key in ['2','4','8']:
    #         motor = int(key)
    #         if motor in motors:
    #             motors.remove(motor)
    #         else:
    #             motors.add(motor)
    #     if key  == 'w':
    #        commands = [2]
    #     if key == 's':
    #         commands = [8]
    #     if key == 'x':
    #         commands = [4]
    #
    #     print(key,list(motors),commands)
    #
    ser.close()


test_steppers()
