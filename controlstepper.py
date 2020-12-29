import serial
import time
import numpy as np
import cv2


def get_chessboard():
    cols = 10
    rows = 8
    chessboard = np.zeros((rows, cols), np.uint8)

    for x in range(0, cols):
        for y in range(0, rows):
            if x % 2 == y % 2:
                chessboard[y, x] = 220
    return cv2.resize(chessboard, (cols * 10, rows * 10), interpolation=cv2.INTER_NEAREST)


def get_chessboard_center(img):
    center = None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = 255 - gray
    # thresh = cv2.threshold(img,60,255,)
    ret, corners = cv2.findChessboardCorners(gray, (7, 9), None)
    # If found, add object points, image points (after refining them)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    print('top')
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        center = np.average(corners2, axis=0)
        # Draw and display the corners
        cv2.drawChessboardCorners(img, (7, 9), corners2, ret)
    return center


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
    # ser = serial.Serial('COM5')  # open serial port
    ser = serial.Serial('/dev/ttyUSB0')  # open serial port
    print(ser.name)  # check which port was really used

    steps_start = np.array([-500, 0, 1000])
    send_commands(ser, steps_start)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    home = 0
    width = 1920
    height = 1000
    background = np.zeros((height, width), np.uint8)
    center_x = int(width / 2)
    center_y = int(height / 2)
    # cv2.circle(background, (center_x, center_y), 50, 255, 1)

    chessboard = get_chessboard()
    background[center_y - 40:center_y + 40, center_x - 50:center_x + 50] = chessboard
    cv2.imshow('background', background)
    cv2.moveWindow('background', 0, 2000)

    while True:
        ret, frame = cap.read()

        # center = get_chessboard_center(frame)
        # print('center', center)
        cv2.imshow('Frame', frame)
        c = cv2.waitKey(1)

        if c == 27:
            break

    for x in range(2):
        home += 100
        steps_start = np.array([home, home, home])
        send_commands(ser, steps_start)
        cv2.imshow('frame', frame)
        cv2.moveWindow('frame', 0, 2000)
        get_chessboard()
        cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()
    ser.close()

    # steps_end = np.array([4950, -3760, -4000])
    # steps_diff = steps_start - steps_end
    # # steps_end = steps_end - steps_diff * 5
    # print(steps_diff)
    #
    # send_commands([-2100, -8450, -8650])
    # send_commands([-7050, -4690, -4790])

    # steps_start * .5 + steps_end + .5
    #

    #
    #

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


test_steppers()
