import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    ### KULIITT
    lower1 = np.array([10, 25, 25], dtype=np.uint8)
    upper1 = np.array([40, 255, 255], dtype=np.uint8)

    ### BIIRUU
    lower2 = np.array([100, 25, 25], dtype=np.uint8)
    upper2 = np.array([130, 255, 255], dtype=np.uint8)

    maskCoklat = cv2.inRange(hsv, lower1, upper1)
    maskBiru = cv2.inRange(hsv, lower2, upper2)

    contours, _ = cv2.findContours(maskBiru, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(max_contour) > 1000:
            
            x, y, w, h = cv2.boundingRect(max_contour)
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            M = cv2.moments(max_contour)
            
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                cv2.putText(frame, f"LOCATION : X={cx}, Y={cy}", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("MASKING AWKOAWAEFJNOADSNFJSFDK", maskCoklat)
    cv2.imshow("HSV AWKOAWAEFJNOADSNFJSFDK", hsv)
    cv2.imshow("OBJ DETECTION ANSKLFNDSAFNCADSNOMC", frame)

    if cv2.waitKey(1) & 0xFF == ord('z'):
        break

cap.release()
cv2.destroyAllWindows()