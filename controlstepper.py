import serial
import time
import numpy as np
import cv2
import math


def get_chessboard(scale):
    cols = 10
    rows = 8
    chessboard = np.zeros((rows, cols), np.uint8)

    for x in range(0, cols):
        for y in range(0, rows):
            if x % 2 == y % 2:
                chessboard[y, x] = 220
    return cv2.resize(chessboard, (cols * scale, rows * scale), interpolation=cv2.INTER_NEAREST)


def get_chessboard_details(img):
    scale = 2
    avg_length = 0
    center = None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = 255 - gray
    h, w = gray.shape
    h = int(h / scale)
    w = int(w / scale)
    gray = cv2.resize(gray, (w, h))

    # thresh = cv2.threshold(img,60,255,)
    ret, corners = cv2.findChessboardCorners(gray, (7, 9), None)
    # If found, add object points, image points (after refining them)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.001)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        center = np.average(corners2, axis=0)
        center = center.reshape(2)
        total_length = 0
        for i in range(63):
            pt = corners2[i, :, :]
            pt = pt.reshape(2)
            total_length += math.hypot(center[0] - pt[0], center[1] - pt[1])
        avg_length = round(total_length / 63 * scale, 3)
        cv2.drawChessboardCorners(img, (7, 9), corners2, ret)
    if center is None:
        return None
    else:
        return center * scale, avg_length


def send_command(ser, motor, steps_in):
    command_string = bytes(5)
    command_string = bytearray(command_string)
    command_string[4] = 113  # FooterID
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

    # print(steps_in, int65536, int256, int1)

    command_string[1] = int1
    command_string[2] = int256
    command_string[3] = int65536
    # print(command_string)
    command_string = bytes(command_string)
    ser.write(command_string)  # write a string


def send_commands(ser, commands):
    send_command(ser, 2, int(commands[0]))
    time.sleep(.1)
    send_command(ser, 4, int(commands[1]))
    time.sleep(.1)
    send_command(ser, 8, int(commands[2]))
    time.sleep(.1)


def get_port_name():
    for port_no in range(5):
        try:
            name = '/dev/ttyUSB' + str(port_no)
            ser = serial.Serial(name)  # open serial port
            ser.close()
            return name
        except serial.serialutil.SerialException:
            pass


def show_background(height, width, scale, center_x, center_y, chessboard):
    background = np.zeros((height, width), np.uint8)
    background[center_y - 4 * scale:center_y + 4 * scale, center_x - 5 * scale:center_x + 5 * scale] = chessboard
    cv2.imshow('background', background)
    cv2.moveWindow('background', 0, 2000)




def get_serial():
    port_name = get_port_name()
    return  serial.Serial(port_name)


def test_steppers():
    # ser = serial.Serial('COM5')
    image_id = 0
    port_name = get_port_name()
    ser = serial.Serial(port_name)

    print('Serial Port Used:', ser.name)  # check which port was really used

    # back/right/left motors
    # steps_start = np.array([3400, -19300, 2000])
    steps_start = np.array([0, 0, 0])
    send_commands(ser, steps_start)
    # steps_start -= 100

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    width = 1920
    height = 1000
    center_x = int(width / 2)
    center_y = int(height / 2)
    # cv2.circle(background, (center_x, center_y), 50, 255, 1)
    scale = 7
    chessboard = get_chessboard(scale)
    margin = 0
    crop_x = int(width * margin)
    crop_y = int(height * margin)
    crop_width = width - crop_x * 2
    crop_height = height - crop_y * 2

    show_background(height, width, scale, center_x, center_y, chessboard)

    last_move_image_id = 0
    last_chessboard_details = np.array([0, 0, 0, 0])
    chessboard_details = np.array([0, 0, 0, 0])
    center = (0, 0)
    blur_factor = 0
    chessboard_size = 0
    while True:
        ret, frame = cap.read()
        if image_id < 40:
            image_id += 1
            continue

        if image_id % 1 != 0:
            image_id += 1
            continue

        frame = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]

        kernel = np.ones((3, 3), np.uint8)
        frame = cv2.dilate(frame, kernel, iterations=1)
        details = get_chessboard_details(frame)
        movement = 0
        if details is not None:
            center, chessboard_size = details
            blur_factor = round(cv2.Laplacian(frame, cv2.CV_64F).var(), 3)
            chessboard_details = np.array([center[0], center[1], blur_factor, chessboard_size])
            movement = abs(chessboard_details - last_chessboard_details)
            movement = movement[0] + movement[1] + movement[3]

        cv2.imshow('Frame', frame)
        cv2.moveWindow('Frame', 2000, 1100)
        c = cv2.waitKey(1)
        # print(image_id, center, blur_factor, steps_start, chessboard_size, movement)

        center_x_offset = crop_width / 2 - center[0]
        center_y_offset = crop_height / 2 - center[1]

        if movement != 0 and movement < 10 and (image_id - last_move_image_id) > 3:
            print(image_id, center, blur_factor, steps_start, chessboard_size, movement)
            print(center_x, center_y, crop_width / 2, crop_height / 2, center_x_offset, center_y_offset)
            center_x += int(round(center_x_offset / 7, 0))
            center_y += int(round(center_y_offset / 7, 0))
            show_background(height, width, scale, center_x, center_y, chessboard)

            steps_to_move = 30
            steps_start[0] += int((chessboard_size - scale * 30 * 1.02) * steps_to_move)
            steps_start[1] += steps_to_move
            steps_start[2] += steps_to_move
            send_commands(ser, steps_start)
            last_move_image_id = image_id
        if c == 27:
            break
        image_id += 1
        last_chessboard_details = chessboard_details
    # for x in range(2):
    #     home += 100
    #     steps_start = np.array([home, home, home])
    #     send_commands(ser, steps_start)
    #     cv2.imshow('frame', frame)
    #     cv2.moveWindow('frame', 0, 2000)
    #     get_chessboard()
    #     cv2.waitKey(0)

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


#test_steppers()
