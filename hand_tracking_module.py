import cv2
import mediapipe as mp
import time

# --------------------------------------------------
# HAND TRACKING MODULE
# --------------------------------------------------
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode                      # static image mode (False for live video)
        self.maxHands = maxHands              # maximum number of hands to detect
        self.detectionCon = detectionCon      # detection confidence threshold
        self.trackCon = trackCon              # tracking confidence threshold

        # MediaPipe Hands initialization
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils  # landmark drawing utility
        self.results = None                      # stores MediaPipe output
        self.handType = None                     # handedness label ("Left" / "Right")

    # --------------------------------------------------
    # HAND DETECTION + LANDMARK DRAWING
    # --------------------------------------------------
    def findHands(self, img, draw=True):
        """
        Detects hands in the frame and optionally draws landmarks.
        MUST be called before findPosition().
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # MediaPipe requires RGB
        self.results = self.hands.process(imgRGB)
        self.handType = None  # reset each frame
        if self.results.multi_hand_landmarks:
            for handLms, handInfo in zip(
                    self.results.multi_hand_landmarks,
                    self.results.multi_handedness):
                # MediaPipe handedness label
                self.handType = handInfo.classification[0].label
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS
                    )
        return img  # IMPORTANT: always return image

    # --------------------------------------------------
    # LANDMARK POSITION + BOUNDING BOX (SAFE EXTENSION)
    # --------------------------------------------------
    def findPosition(self, img, handNo=0, draw=True):
        """
        Returns:
        - lmList : list of [id, x, y] landmarks (USED BY VOLUME & MOUSE)
        - bbox   : (xmin, ymin, xmax, ymax) bounding box (USED BY VIRTUAL MOUSE)
        """
        lmList = []      # landmark list (same as old behavior)
        bbox = None      # bounding box (NEW, optional)
        # Ensure hands are detected
        if self.results and self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                xList = []  # store all x values for bbox
                yList = []  # store all y values for bbox
                h, w, c = img.shape
                # Loop through 21 landmarks
                for id, lm in enumerate(myHand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # OLD behavior preserved
                    lmList.append([id, cx, cy])
                    # NEW: collect for bounding box
                    xList.append(cx)
                    yList.append(cy)
                    if draw:
                        cv2.circle(img, (cx, cy), 5,
                                    (255, 0, 255), cv2.FILLED)
                # Compute bounding box (NEW, non-breaking)
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bbox = (xmin, ymin, xmax, ymax)
        # IMPORTANT:
        # - Volume code must UNPACK → lmList, _
        # - Virtual mouse uses both lmList, bbox
        return lmList, bbox
