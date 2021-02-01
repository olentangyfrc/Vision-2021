import time
import imutils

import cv2

from networktables import NetworkTables

NetworkTables.initialize(server='192.168.1.193')
sd = NetworkTables.getTable('SmartDashboard')


time.sleep(2)

print("I am looking for a yellow ball")
yellowLower = (20, 100, 100)
yellowUpper = (30, 255, 255)


cap = cv2.VideoCapture(0)
print("Getting camera image...")
while 1:

    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
    

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    if len(cnts) > 0:
        
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if radius > 10:

            cv2.circle(img, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(img, center, 5, (0, 0, 255), -1)

            direction = ''
            if x > 440:
                direction = "to the right"
            elif x < 200:
                direction = "to the left"
            else:
                direction = 'straight ahead'
            #approx distance by measuring radius
            distance = ''
            if radius > 110:
                distance = "very close"
            elif radius > 85:
                distance = "near"
            elif radius > 20:
                distance = "not very close"
            else:
                distance = "far"
            print("I can see a ball!, it is  " + distance + " and " + direction)
            sd.putBoolean('SeeBall', True)
            sd.putNumber('BallRadius', radius)
            sd.putString('BallDirection', direction)

    else:
        print("I cannot see a ball")
        sd.putBoolean('SeeBall', False)

