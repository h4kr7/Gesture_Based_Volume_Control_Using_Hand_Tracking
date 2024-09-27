import cv2
import hand_tracking_module as htm
import math
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # pip install pycaw

# define height and width of the camera
width_of_camera, height_of_camera = 640, 480

cam = cv2.VideoCapture(0)
detector = htm.handDetector(detectionCon=0.7)

cam.set(3, width_of_camera)
cam.set(4, height_of_camera)

##########################################################################################
# copy from github pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()  # not need
# volume.GetMasterVolumeLevel()  # not need
# print(volume.GetVolumeRange())  # find volume range
# volume.SetMasterVolumeLevel(-65.25, None)  # volume range low --> -65.25, high --> 0
##########################################################################################

# to control the volume
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# volume bar
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cam.read()
    detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # print(lmList[4], lmList[8])  # helps to see the index_finger and thumb direction
        x1, y1 = lmList[4][1], lmList[4][2]  # thumb dimensions
        x2, y2 = lmList[8][1], lmList[8][2]  # index finger dimensions
        cx, cy = (x1 + x2) // 2, (
            y1 + y2
        ) // 2  # between thumb and index finger dimensions

        cv2.circle(
            img, (x1, y1), 10, (255, 0, 255), cv2.FILLED
        )  # creating circle on thumb
        cv2.circle(
            img, (x2, y2), 10, (255, 0, 255), cv2.FILLED
        )  # creating circle on index finger
        # cv2.line(img, 1st point, 2nd point,color , thickness)  # dimensions of line
        cv2.line(
            img, (x1, y1), (x2, y2), (255, 0, 255), 3
        )  # creating line between index finger and thumb
        cv2.circle(
            img, (cx, cy), 5, (255, 0, 255), cv2.FILLED
        )  # creating circle between index finger and thumb

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)  # find length between thumb and index finger

        # Hand range 20 - 190
        # Volume Range -65.25 - 0

        vol = np.interp(
            length, [20, 190], [minVol, maxVol]
        )  # helps to attach the volume to hands
        volBar = np.interp(
            length, [20, 190], [400, 100]
        )  # helps to fill volume bar according to hands
        volPer = np.interp(
            length, [20, 190], [0, 100]
        )  # helps to attach volume bar percentage
        print(int(length), vol)  # print length and volume according to hand
        volume.SetMasterVolumeLevel(vol, None)

        if length < 20:
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

    # rectangle shape to show volume
    # rectangle(img, (x1,y1),(x2,y2), color, thickness)  # rectangle parameter
    cv2.rectangle(
        img, (50, 100), (85, 400), (255, 0, 0), 3
    )  # create rectangle for volume bar
    cv2.rectangle(
        img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED
    )  # create another rectangle to fill volume bar
    cv2.putText(
        img, f"{int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3
    )  # add text for showing volume bar percentage

    cv2.imshow("Gesture Volume control", img)
    cv2.waitKey(1)

    if (
        cv2.getWindowProperty("Gesture Volume control", cv2.WND_PROP_VISIBLE) < 1
    ):  # exit the window by cross key
        break

cam.release()
cv2.destroyAllWindows()