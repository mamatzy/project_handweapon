import cv2 as cv
import numpy as np
 
cap = cv.VideoCapture(0)

# Custom warna deteksi biru 
# blue_low = np.uint8([[[213,219,125]]])
# hsv_blue_low = cv.cvtColor(blue_low,cv.COLOR_BGR2HSV)
# print('blue lower : ', hsv_blue_low)

# blue_up = np.uint8([[[212,25,66]]])
# hsv_blue_up = cv.cvtColor(blue_up,cv.COLOR_BGR2HSV)
# print('blue upper : ', hsv_blue_up)

while(1):
 
    # Take each frame
    _, frame = cap.read()
 
    # Convert BGR to HSV
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
 
    # define range of blue color in HSV

    # Custom abal abal akowawakoawkaow
    # lower_blue = np.array([hsv_blue_low[0][0][0], hsv_blue_low[0][0][1], hsv_blue_low[0][0][2]])
    # upper_blue = np.array([hsv_blue_up[0][0][0], hsv_blue_up[0][0][1], hsv_blue_up[0][0][2]])
 
    lower_blue = np.array([30, 50, 50], dtype=np.uint8)
    upper_blue = np.array([90, 255, 255], dtype=np.uint8)

    # Threshold the HSV image to get only blue colors
    mask = cv.inRange(hsv, lower_blue, upper_blue)
 
    # Bitwise-AND mask and original image
    res = cv.bitwise_and(frame,frame, mask= mask)
 
    cv.imshow('frame',frame)
    cv.imshow('mask',mask)
    cv.imshow('res',res)
    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
 
cv.destroyAllWindows()