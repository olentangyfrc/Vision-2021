import time
import imutils
import datetime
import cv2

from networktables import NetworkTables

NetworkTables.initialize(server='192.168.1.193')
sd = NetworkTables.getTable('SmartDashboard')

time.sleep(5)

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def SendtoNT(ballvisible, distance, direction):
    sd.putBoolean('SeeBall', ballvisible)
    sd.putNumber('BallDistance', distance)
    sd.putString('BallDirection', direction)
    sd.putString('CoprocessorTime', str(datetime.datetime.now()))



# set color range of what to look for
print("I am looking for a yellow ball")
yellowLower = (20, 110, 110)
yellowUpper = (30, 255, 255)

# load the camera image
cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
print("Getting camera image...")
while 1:
    # read the image, change the colors so it's easier to find what we're looking for
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # look for objects of the color range we designated
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)

    # look for shapes in the color we're looking for
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # if it sees a circular object that is yellow, do this
    if len(cnts) > 0:
       # print(len(cnts))
        c = max(cnts, key=cv2.contourArea)

        # draw a circle on the object we found
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)



        if radius > 400:
            print("Ball too close")
            SendtoNT(True, .5, center)
        # set minimum size of circle

        elif radius > 10:
            #print("radius " + str(radius))
            cv2.circle(img, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(img, center, 5, (0, 0, 255), -1)

            # using the x, y of the center of the cicle, is the object to the left, right, or straight ahead from the camera?
            # the numbers are pixels. image is 640x480, numbered 0 to 640 on the X axis.
            direction = ''
            if x > 880:
                direction = "right"
            elif x < 400:
                direction = "left"
            else:
                direction = "center"

            # approximate distance by measuring radius. The bigger the radius, the closer it is.
            distance = round(380/radius, 2)

            # print to console what it sees
            print("I can see a ball! It is approximately " + str(distance) + " feet away and to the " + direction)

            # send to ShuffleBoard whether we see the object we're looking for, how far it is and which direction
            SendtoNT(True, distance, direction)
            #sd.putBoolean('SeeBall', True)
            #sd.putNumber('BallDistance', distance)
            #sd.putString('BallDirection', direction)
            #sd.putString('CoprocessorTime', str(datetime.datetime.now()))
    else:

        # print to console that it does not see the object and send to Shuffleboard
        print("I cannot see a ball")
        SendtoNT(False, 0, "unknown")
        #sd.putBoolean('SeeBall', False)
        #sd.putString('CoprocessorTime', str(datetime.datetime.now()))
#    cv2.imshow('img', mask)
#    k = cv2.waitKey(1)
