import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)

# default biru
h_val, s_val, v_val = 110, 150, 150

while True:
    _, frame = cap.read()
    frame = cv.flip(frame, 1)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Menentukan range 
    lower_blue = np.array([h_val - 20, 50, 50])
    upper_blue = np.array([h_val, s_val, v_val])

    mask = cv.inRange(hsv, lower_blue, upper_blue)
    res = cv.bitwise_and(frame, frame, mask=mask)

    # Tampilkan status HSV
    status = f"H:{h_val} S:{s_val} V:{v_val}"
    cv.putText(frame, status, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv.imshow('Original & Status', frame)
    cv.imshow('Mask (Hitam Putih)', mask)
    # cv.imshow('Hasil (Warna Terfilter)', res)

    key = cv.waitKey(1) & 0xFF
    
    if key == ord('z'): 
        break
    
    # Kontrol HUE (0-179)
    elif key == ord('q'): h_val = min(179, h_val + 1)
    elif key == ord('a'): h_val = max(0, h_val - 1)
    
    # Kontrol SATURATION (0-255)
    elif key == ord('w'): s_val = min(255, s_val + 5)
    elif key == ord('s'): s_val = max(0, s_val - 5)
    
    # Kontrol VALUE/Brightness (0-255)
    elif key == ord('e'): v_val = min(255, v_val + 5)
    elif key == ord('d'): v_val = max(0, v_val - 5)

cap.release()
cv.destroyAllWindows()