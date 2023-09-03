import os

import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1280, 720

folderPath = "presentation"

cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)


pathImages = sorted(os.listdir(folderPath), key=len)

#variables
imgNumber = 0
hs, ws, = int(120*1), int(213*1)
gestureThreshold = 300

buttonPress = False
buttonCounter = 0
buttonDelay = 10
annotations = [[]]
ann_counter = -1
ann_start = False

detector = HandDetector(detectionCon=0.8, maxHands=1)


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands and not buttonPress:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx,cy = hand['center']

        lmList = hand['lmList']

        #constrain values for easier drawing
        indexFinger = lmList[8][0], lmList[8][1]
        xVal = int(np.interp(lmList[8][0], [width//2, w-50], [0, width]))
        yVal = int(np.interp(lmList[8][1], [200, height-200], [0, h]))
        indexFinger = xVal, yVal

        #Gestures
        if cy <= gestureThreshold:
            ann_start = False
            #Gesture 1 - Left slide
            if fingers == [1, 0, 0, 0, 0]:
                ann_start = False
                if imgNumber > 0:
                    print('left')
                    annotations = [[]]
                    ann_counter = -1
                    buttonPress = True
                    imgNumber -= 1

            #Gesture 2 - Right slide
            if fingers == [0, 0, 0, 0, 1]:
                ann_start = False
                if imgNumber < len(pathImages) - 1:
                    print('right')
                    annotations = [[]]
                    ann_counter = -1   
                    buttonPress = True
                    imgNumber += 1
            
        #Gesture 3 - show pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            ann_start = False
        
        # Gesture 4 - draw
        if fingers == [0, 1, 0, 0, 0]:
            if not ann_start:
                ann_start = True
                ann_counter += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[ann_counter].append(indexFinger)
        else:
            ann_start = False
        
        #Gesture 5 - erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                annotations.pop(-1)
                if ann_counter > 0:
                    ann_counter -= 1
                buttonPress = True
        
        # Gesture 5 - erase
        if fingers == [0, 1, 1, 1, 1]:
            annotations = [[]]
            ann_counter = 0
            buttonPress = True
    else:
        ann_start = False

    #button press delay mechanic
    if buttonPress:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPress = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)

    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall

    cv2.imshow("Presentation", imgCurrent)
    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
