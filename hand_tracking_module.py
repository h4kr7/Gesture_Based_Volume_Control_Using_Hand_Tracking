# pip install opencv-python
import cv2

# pip install mediapipe
import mediapipe as mp
import time  # to check framerate


class handDetector:
    def __init__(
        self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5
    ):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Initialise Hand
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode,
            self.maxHands,
            self.modelComplex,
            self.detectionCon,
            self.trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # convert color
        self.result = self.hands.process(imgRGB)  # converted color result

        # Draw dots in hands
        if self.result.multi_hand_landmarks:
            for handlandmark in self.result.multi_hand_landmarks:
                if draw:
                    # self.mpDraw.draw_landmarks(img, handlandmark)  # for dots only
                    self.mpDraw.draw_landmarks(
                        img, handlandmark, self.mpHands.HAND_CONNECTIONS
                    )  # for lines and dots
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.result.multi_hand_landmarks:
            myHand = self.result.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id,lm)  # find the location on the landmark on hand
                h, w, c = img.shape  # height, weight, channels
                cx, cy = int(lm.x * w), int(lm.y * h)  # convert into pixels
                # print(id, cx, cy)  # check the correct position in pixels
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lmList


def main():
    # initialize time for FPS
    previous_time = 0
    current_time = 0

    # open Camera-0
    cap = cv2.VideoCapture(0)

    detector = handDetector()

    while True:
        # read the camera
        success, img = cap.read()

        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        # check FPS rate
        current_time = time.time()
        fps = 1 / (current_time - previous_time)
        previous_time = current_time

        # (parameters) cv2.putText(img, text, location, font, size, color, thickness)
        cv2.putText(
            img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3
        )

        cv2.imshow("Hand Tracking", img)
        cv2.waitKey(1)  # waiting time 1 milisecond


if __name__ == "__main__":
    main()