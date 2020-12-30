import cv2 as cv2
import imutils
import numpy as np
import math
import linemodel
import controlstepper


# define names of each possible ArUco tag OpenCV supports
# noinspection PyUnresolvedReferences
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}


# noinspection PyUnresolvedReferences
def get_background(height, width, size, scale):
    aruco_dict = get_aruco_dict()
    tag = np.zeros((300, 300, 1), dtype="uint8")
    background = np.zeros((height, width), np.uint8)
    background = background + 255

    for x in range(192):
        for y in range(100):
            if x % 2 == y % 2:
                marker_id = x
            else:
                marker_id = y + 250
            # todo, what is the tag and 1?
            marker = cv2.aruco.drawMarker(aruco_dict, marker_id, size * scale, tag, 1)
            mx = int(size * scale * 1.25 * x)
            my = int(size * scale * 1.25 * y)

            background[my * scale:my + 8 * scale, mx * scale:mx + 8 * scale] = marker

    return background


# noinspection PyUnresolvedReferences
def get_aruco_dict():
    return cv2.aruco.Dictionary_get(ARUCO_DICT['DICT_6X6_1000'])


def get_pixel_center(markers):
    pixel_centers = []
    for marker1, pixel1 in markers.items():
        for marker2, pixel2 in markers.items():
            if marker1 < marker2:
                marker_units = marker2 - marker1
                marker_scale = pixel2 - pixel1
                pixels_to_center = 100 - pixel2
                offset = pixels_to_center / marker_scale * marker_units
                pixel_centers.append(marker2 * 10 + offset)

    return np.average(pixel_centers)



# noinspection PyUnresolvedReferences
def get_location(frame, width, height):
    background_x = 0
    background_y = 0
    marker_size = 0

    center_x = int(width / 2)
    center_y = int(height / 2)
    last_mean_angle = 0
    radius = 100
    aruco_dict = get_aruco_dict()
    corners = None

    frame = frame[center_y - radius:center_y + radius, center_x - radius:center_x + radius, :]

    # noinspection PyUnresolvedReferences
    parameters = cv2.aruco.DetectorParameters_create()
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    total_markers = 0
    lengths = []
    x_markers = {}
    y_markers = {}
    for j in range(2):
        if j == 1:
            frame = imutils.rotate(frame, last_mean_angle)
        corners, ids, rejected_img_points = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

        total_markers = 0
        angles = []

        if np.all(ids is not None):  # If there are markers found by detector
            total_markers = len(ids)
            for i in range(0, len(ids)):  # Iterate in markers
                x1 = corners[i][0][0][0]
                y1 = corners[i][0][0][1]
                x2 = corners[i][0][1][0]
                y2 = corners[i][0][1][1]
                x3 = corners[i][0][2][0]
                y3 = corners[i][0][2][1]
                x4 = corners[i][0][3][0]
                y4 = corners[i][0][3][1]

                line_model = linemodel.LineModel(((x1, y1), (x2, y2)))
                angle = line_model.get_angle()
                if j == 1:
                    lengths.append(math.hypot(x1-x2,y1-y2))
                    lengths.append(math.hypot(x2 - x3, y2 - y3))
                    lengths.append(math.hypot(x3 - x4, y3 - y4))
                    lengths.append(math.hypot(x4 - x1, y4 - y1))

                if angle > 180:
                    angle = angle - 360
                angles.append(angle)
                if j == 1:
                    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
                    key = ids[i][0]
                    cv2.putText(frame, str(key), org=(x1, int(y1 + 16)), fontFace=font, fontScale=1, thickness=1,
                                color=(0, 0, 255))
                    #todo if I want to raise accurary I could put in the 3 other points.
                    if key >= 250:
                        y_markers[key-250] = y1
                    else:
                        x_markers[key] = x1

            # Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
            # rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
            # 														   distortion_coefficients)
            # (rvec - tvec).any()  # get rid of that nasty numpy value array error
            last_mean_angle = np.mean(angles)


        background_x = get_pixel_center(x_markers)
        background_y = get_pixel_center(y_markers)


    cv2.aruco.drawDetectedMarkers(frame, corners)  # Draw A square around the markers
    frame = cv2.resize(frame, (400, 400))
    cv2.imshow('Frame', frame)
    # cv2.imshow('background', background)
    cv2.moveWindow('Frame', 2000, 1100)

    marker_size = np.average(lengths)
    text = ['background Total,x,y,marker_size',total_markers,round(background_x,2),round(background_y,2),round(marker_size,2)]

    return background_x, background_y, marker_size, text


def follow_path():
    scale = 1
    size = 8
    background = get_background(1000, 1920, size, scale)
    cv2.imshow('background', background)
    cv2.moveWindow('background', 0, 2000)
    width = 640
    height = 480
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    marker_size_target = 33.5
    #steps_start = [506, 0, 0]
    #steps_start = [3405,-4700,0]
    steps_start = [7790,-4700,-4700]

    ser = controlstepper.get_serial()
    controlstepper.send_commands(ser, steps_start)
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    target_x = 960
    target_y = 500
    last_location = None
    movement_threshold = .05
    while True:
        ret, frame = cap.read()
        background_x, background_y, marker_size,text = get_location(frame, width, height)
        cv2.waitKey(1)
        if math.isnan(background_x) or math.isnan(background_y) or math.isnan(marker_size):
            continue

        location = np.array([background_x, background_y, marker_size])
        if last_location is None:
            last_location = location
            movement = 100
        else:
            movement = sum(abs(location - last_location))

        if movement < movement_threshold:
            #movement_threshold = .06 #make it bigger after homing.
            marker_size_diff = marker_size_target - marker_size
            steps_to_move = 50
            steps_start[0] += int(marker_size_diff * steps_to_move ) * -1.5
            if marker_size_diff < .1:
                pass
                if steps_start[1] < 10000:
                    pass
                    #steps_start[1] += steps_to_move
                #steps_start[2] += steps_to_move
            print(movement,steps_start,text)
            controlstepper.send_commands(ser, steps_start)
        else:
            print(movement)
        last_location = location




follow_path()
