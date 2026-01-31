# Controls:-
    #  Cursor Move → Move index finger
    #  Left Click → Index + thumb pinch
    #  Right Click → Middle finger + thumb pinch
    #  Scroll → Open palm + move hand up/down
    #  Vomume Control -> middle + thumb hold and vol - index and thumb
    #  Press  Q to quit 

import cv2
import time
import numpy as np
import hand_tracking_module as htm # for full hand tracking
import autopy  # for mouse control
import pyautogui  # for scrolling
import math # for using hypotenuse func
# pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # for volume

# CAMERA SETUP 
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

frameR = 100  # frame reduction (dead zone to avoid edge jitter)
# CLICK
clickDown = False        # prevents repeated clicks
# GESTURE THRESHOLDS 
PINCH_DISTANCE = 20      # thumb + index pinch
RELEASE_DISTANCE = 35    # fingers separated
# SCREEN SIZE 
wScr, hScr = autopy.screen.size()  # system resolution
# MOUSE SMOOTHING 
smoothening = 6          # higher = smoother, lower = faster
plocX, plocY = 0, 0      # previous mouse location
clocX, clocY = 0, 0      # current mouse location
# SCROLL VARIABLES 
prevScrollY = 0
SCROLL_GAIN = 2.0        # scroll speed multiplier
SCROLL_DEADZONE = 6      # ignore tiny movements
# RIGHT CLICK 
rightClickDown = False   # debounce for right click

## Volume variables 
pTime = 0
detector = htm.handDetector(detectionCon=0.7,maxHands=1)
devices = AudioUtilities.GetSpeakers()  # from github pycaw lib for volume 
interface = devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volPer = 0.0   # default volume percentage when no hand detected
volBar = 400   # default bar position (empty bar)
volumeActive = False  # pinch-gated volume control state

# for fps 
pTimeFPS = 0   # FPS timer only

while True:
    # Capture frame from camera
    success, img = cap.read()                  # read webcam frame
    if not success:
        break                           # if frame not captured

    # Detect hand and landmarks
    img = detector.findHands(img)              # detect hands + draw
    lmList, bbox = detector.findPosition(img,draw=False)  # get landmarks + bounding box

    # Due to non-mirrored camera feed, MediaPipe reports hands reversed.
    # if your camera is mirrored change this by replacing "Left" and "Right" in this program

    # Right (MediaPipe) → Physical LEFT hand → Volume
    if len(lmList) != 0 and detector.handType == "Right": # process ONLY our left hand
        # landmarks
        x1, y1 = lmList[4][1], lmList[4][2] # thumb 
        x2, y2 = lmList[8][1], lmList[8][2] # index finger
        x3, y3 = lmList[12][1], lmList[12][2] # middle finger
        pinchDist = math.hypot(x3 - x1, y3 - y1) # thumb + middle activation 
        if pinchDist < 25:
            volumeActive = True # pinch ON → start volume control
        elif pinchDist > 40:
            volumeActive = False # pinch OFF → stop volume control

        length = math.hypot(x2 - x1, y2 - y1) # Vol distance between thumb and index finger
        if volumeActive:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

            volPer = np.interp(length, [10, 150], [0.0, 1.0])  # map hand distance to volume percentage
            volPer = np.clip(volPer, 0.0, 1.0)  # clamp volume to avoid overflow
            volBar = np.interp(length, [10, 150], [400, 150])  # map distance to bar height (inverted Y-axis)
            print(detector.handType,int(length), int(volPer * 100))  # debug: distance and volume %

            volume.SetMasterVolumeLevelScalar(volPer, None) # set system volume in real time

            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)  # draw volume bar outline
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)  # draw filled volume bar
            cv2.putText(img, f'{int(volPer * 100)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)  # show volume %
            cv2.putText(img, "VOLUME ACTIVE", (20, 90),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        else:
            cv2.putText(img, "VOLUME INACTIVE", (300, 90),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    # Left (MediaPipe) → Physical RIGHT hand → Mouse
    if len(lmList) != 0 and detector.handType == "Left":
        cv2.putText(img, "MOUSE ACTIVE", (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
        # KEY LANDMARKS 
        x1, y1 = lmList[8][1], lmList[8][2]    # index fingertip
        x2, y2 = lmList[4][1], lmList[4][2]    # thumb fingertip
        # draw fingertip circles
        cv2.circle(img, (x1, y1), 8, (255, 0, 255), cv2.FILLED)  # index tip
        cv2.circle(img, (x2, y2), 8, (255, 0, 255), cv2.FILLED)  # thumb tip
        # distance between index and thumb
        fingersDistance = np.hypot(x2 - x1, y2 - y1)  # pinch distance

        # PALM DETECTION 
        index_tip = lmList[8][2]              # index fingertip y
        middle_tip = lmList[12][2]            # middle fingertip y
        ring_tip = lmList[16][2]              # ring fingertip y
        pinky_tip = lmList[20][2]             # pinky fingertip y
        index_knuckle = lmList[6][2]           # index knuckle y
        middle_knuckle = lmList[10][2]         # middle knuckle y
        ring_knuckle = lmList[14][2]           # ring knuckle y
        pinky_knuckle = lmList[18][2]          # pinky knuckle y

        palm = (                               # open palm condition
            index_tip < index_knuckle and
            middle_tip < middle_knuckle and
            ring_tip < ring_knuckle and
            pinky_tip < pinky_knuckle
        )
        # PALM SCROLL 
        if detector.handType == "Left" and palm and fingersDistance > RELEASE_DISTANCE:
            cv2.putText(img, "PALM SCROLL", (260, 80),   # mode text
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            if prevScrollY != 0:
                scrollDelta = prevScrollY - index_tip   # vertical hand move
                if abs(scrollDelta) > SCROLL_DEADZONE:  # ignore small jitter
                    pyautogui.scroll(int(-scrollDelta * SCROLL_GAIN))  # scroll
            prevScrollY = index_tip                     # update previous y
        else:
            prevScrollY = 0                             # reset scroll state

        # CLICK MODE 
        if fingersDistance < PINCH_DISTANCE:             # pinch detected
            cv2.line(img, (x1, y1), (x2, y2),
                    (0, 255, 0), 3)                      # visual feedback
            if not clickDown:
                autopy.mouse.click()                     # single left click
                clickDown = True                         # debounce lock
        # release pinch
        elif fingersDistance > RELEASE_DISTANCE:
            clickDown = False                            # unlock click

        # RIGHT CLICK 
        middle_x, middle_y = lmList[12][1], lmList[12][2]  # middle fingertip
        middle_thumb_dist = np.hypot(middle_x - x2, middle_y - y2)  # dist
        if middle_thumb_dist < 20 and not rightClickDown:
            autopy.mouse.click(button=autopy.mouse.Button.RIGHT)  # right click
            rightClickDown = True                                 # debounce lock
        elif middle_thumb_dist > 30:
            rightClickDown = False                                # unlock

        # MOVE MODE 
        if (fingersDistance > RELEASE_DISTANCE and not palm and not clickDown):
            cv2.putText(img, "MOVE", (260, 120),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            if bbox:
                xmin, ymin, xmax, ymax = bbox        # bounding box
                # draw control frame
                cv2.rectangle(img,(frameR, frameR),(wCam - frameR, hCam - frameR),
                    (255, 0, 255),2)
                # convert camera coords to screen coords
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                # smooth mouse movement
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                # move mouse
                autopy.mouse.move(wScr - clocX, clocY)
                plocX, plocY = clocX, clocY

    # FPS DISPLAY 
    cTime = time.time()                                 # current frame time
    fps = 1 / (cTime - pTimeFPS) if cTime != pTimeFPS else 0 # fps calc
    pTimeFPS = cTime                                      # update prev time
    cv2.putText(img, f"FPS: {int(fps)}", (450,40),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    # DISPLAY WINDOW 
    cv2.imshow("VisionTouch OS", img)                   # show frame
    if cv2.waitKey(1) & 0xFF == ord('q'):                # press q to quit
        break
cap.release()
cv2.destroyAllWindows()
