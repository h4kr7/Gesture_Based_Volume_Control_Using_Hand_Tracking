import cv2
import hand_tracking_module as htm
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize camera
width_of_camera, height_of_camera = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, width_of_camera)
cam.set(4, height_of_camera)
detector = htm.handDetector(detectionCon=0.7)

# to control the volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# volume range
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

    # check the length of thumb and index finger
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # draw circles on thumb and index finger
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # Hand range 20—190
        # Volume Range -65.25—0

        # convert the length into volume
        vol = np.interp(length, [20, 190], [minVol, maxVol])
        volBar = np.interp(length, [20, 190], [400, 100])
        volPer = np.interp(length, [20, 190], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        # to check the length of thumb and index finger
        if length < 20:
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

    # create volume bar
    cv2.rectangle(img, (50, 100), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(
        img, f"{int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3
    )

    cv2.imshow("Gesture Volume control", img)
    cv2.waitKey(1)

    # exit the window by "X" button
    if cv2.getWindowProperty("Gesture Volume control", cv2.WND_PROP_VISIBLE) < 1:
        break

cam.release()
cv2.destroyAllWindows()
