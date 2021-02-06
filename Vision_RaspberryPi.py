import time
import imutils
import datetime
import cv2
import math

from networktables import NetworkTables

NetworkTables.initialize(server='192.168.1.193')
sd = NetworkTables.getTable('SmartDashboard')

time.sleep(5)

#set color range of what to look for
print("I am looking for a yellow ball")
yellowLower = (20, 100, 100)
yellowUpper = (30, 255, 255)

#load the camera image
cap = cv2.VideoCapture(0)
print("Getting camera image...")
while 1:
    #read the image, change the colors so it's easier to find what we're looking for
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #look for objects of the color range we designated
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
    
    #look for shapes in the color we're looking for
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None


    #if it sees a circular object that is yellow, do this
    if len(cnts) > 0:
        
        c = max(cnts, key=cv2.contourArea)

        #draw a circle on the object we found
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)

        #set minimum size of circle
        if radius > 10:

            cv2.circle(img, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(img, center, 5, (0, 0, 255), -1)

            #using the x, y of the center of the cicle, is the object to the left, right, or straight ahead from the camera?
            # the numbers are pixels. image is 640x480, numbered 0 to 640 on the X axis.
            direction = '';
            double distOfSector = 640/7;
            if (x < distOfSector)
                direction = "far left";
            elif (x < 2 * distOfSector)
                direction = "left";
            elif (x < 3 * distOfSector)
                direction = "middle left";
            elif (x < 4 * distOfSector)
                direction = "middle";
            elif (x < 5 * distOfSector)
                direction = "middle right";
            elif (x < 6 * distOfSector)
                direction = "right";
            elif (x < 7 * distOfSector)
                direction = "far right";
            #approximate distance by measuring radius. The bigger the radius, the closer it is.
            distance = ''
            if radius > 110:
                distance = "very close"
            elif radius > 85:
                distance = "near"
            elif radius > 20:
                distance = "not very close"
            else:
                distance = "far"

            #finds angle from center of x-axis, or 320, first converts to radians to use math.atan func, then convert
            #back to degrees
            double XangleFromCenter = (180 / math.pi) * math.atan((y / abs(320 - x) ) * (math.pi / 180));

            #print to console what it sees
            print("I can see a ball!, it is  " + distance + " and to the " + direction)


            #send to ShuffleBoard whether we see the object we're looking for, how far it is and which direction
            sd.putBoolean('SeeBall', True)
            sd.putNumber('BallRadius', radius)
            sd.putString('BallDirection', direction)
            sd.putString('pitime', str(datetime.datetime.now()))
    else:

        #print to console that it does not see the object and send to Shuffleboard
        print("I cannot see a ball")
        sd.putBoolean('SeeBall', False)
        sd.putString('pitime', str(datetime.datetime.now()))

