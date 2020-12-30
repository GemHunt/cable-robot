import imutils
import numpy as np
import cv2
import time
import linemodel


# define names of each possible ArUco tag OpenCV supports
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

def get_background(height, width, size,scale,arucoDict):
	tag = np.zeros((300, 300, 1), dtype="uint8")
	background = np.zeros((height, width), np.uint8)
	background = background+255

	for x in range(192):
		for y in range(100):
			if x % 2 == y % 2:
				marker_id = x
			else:
				marker_id = y + 250
			#todo, what is the tag and 1?
			marker = cv2.aruco.drawMarker(arucoDict, marker_id, size * scale, tag, 1)
			mx = int(size * scale * 1.25 * x)
			my = int(size * scale * 1.25 * y)

			background[my * scale:my + 8 * scale, mx * scale:mx + 8 * scale] = marker

	return background




arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT['DICT_6X6_1000'])
scale = 1
size = 8

background = get_background(1000,1920,size, scale,arucoDict)

cv2.imshow('background', background)
cv2.moveWindow('background', 0, 2000)


width = 640
height = 480
center_x = int(width / 2)
center_y = int(height / 2)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
# Check if the webcam is opened correctly
if not cap.isOpened():
	raise IOError("Cannot open webcam")
last_mean_angle = 0
while True:
	start_time = time.time()
	ret, frame = cap.read()
	radius = 80
	frame = frame[center_y-radius:center_y+radius,center_x-radius:center_x+radius,:]

	parameters = cv2.aruco.DetectorParameters_create()
	for j in range(2):
		if j == 1:
			frame = imutils.rotate(frame, last_mean_angle )
		corners, ids, rejected_img_points = cv2.aruco.detectMarkers(frame, arucoDict, parameters=parameters)

		total_markers = 0
		angles = []
		if np.all(ids is not None):  # If there are markers found by detector
			total_markers = len(ids)
			for i in range(0, len(ids)):  # Iterate in markers
				x1 = corners[i][0][0][0]
				y1 = corners[i][0][0][1]
				x2 = corners[i][0][1][0]
				y2 = corners[i][0][1][1]
				line_model = linemodel.LineModel(((x1,y1),(x2,y2)))
				angle = line_model.get_angle()

				if angle > 180:
					angle = angle - 360
				angles.append(angle)
				if j == 1:
					font = cv2.FONT_HERSHEY_COMPLEX_SMALL
					key = ids[i][0]
					cv2.putText(frame,str(key),org= (x1, int(y1+16)),fontFace= font,fontScale=1,thickness=1,color=(0,0,255))
					if key >= 250:
						print(key,y1,'y')
					else:
						print(key, x1,'x')

				# Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
				# rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
				# 														   distortion_coefficients)
				# (rvec - tvec).any()  # get rid of that nasty numpy value array error
			last_mean_angle = np.mean(angles)


	cv2.aruco.drawDetectedMarkers(frame, corners)  # Draw A square around the markers
	frame = cv2.resize(frame,(400,400))
	cv2.imshow('Frame', frame)
	#cv2.imshow('background', background)
	cv2.moveWindow('Frame', 2000, 1100)
	cv2.waitKey(1)

	print(time.time()-start_time,'Total markers found:',total_markers,round(last_mean_angle,0))









