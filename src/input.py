import cv2
import numpy as np

cap = cv2.VideoCapture(0)
current_state = "KOSONG"

while True:
    ret, frame = cap.read()

    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    
    h_frame, w_frame = frame.shape[:2]
    
    w_half = w_frame // 2
    h_half = h_frame // 2
    
    # WASD Zone
    w_step = w_half // 3
    h_step = h_half // 2
    
    # Format koordinat: (x1, y1, x2, y2)
    zones = {
        "W": (w_step, h_half, w_step * 2, h_half + h_step),
        "A": (0, h_half + h_step, w_step, h_frame),
        "S": (w_step, h_half + h_step, w_step * 2, h_frame),
        "D": (w_step * 2, h_half + h_step, w_half, h_frame),
        "MOUSE": (w_half, h_half, w_frame, h_frame)
    }

    # Gambar kotak zona di layar sebagai panduan visual
    for name, (x1, y1, x2, y2) in zones.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, name, (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    ### KULIITT
    lower1 = np.array([5, 80, 80], dtype=np.uint8)
    upper1 = np.array([40, 255, 255], dtype=np.uint8)

    ### BIIRUU
    lower2 = np.array([100, 100, 100], dtype=np.uint8)
    upper2 = np.array([130, 255, 255], dtype=np.uint8)

    maskCoklat = cv2.inRange(hsv, lower1, upper1)
    maskBiru = cv2.inRange(hsv, lower2, upper2)

    contours, _ = cv2.findContours(maskCoklat, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Default lokasi jika tidak ada objek
    detected_zone = "KOSONG"

    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(max_contour) > 1000:
            x, y, w, h = cv2.boundingRect(max_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            M = cv2.moments(max_contour)
            
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                # Cek apakah titik tengah objek (cx, cy) berada di dalam salah satu zona
                for name, (x1, y1, x2, y2) in zones.items():
                    if x1 <= cx <= x2 and y1 <= cy <= y2:
                        detected_zone = name
                        break # Hentikan loop jika sudah ketemu zonanya

    if detected_zone != current_state:
        print(f"Perintah: {detected_zone}")
        current_state = detected_zone

    # Tampilkan status di layar agar mudah dilihat
    cv2.putText(frame, f"STATUS: {current_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("MASKING AWKOAWAEFJNOADSNFJSFDK", maskCoklat)
    cv2.imshow("OBJ DETECTION ANSKLFNDSAFNCADSNOMC", frame)

    if cv2.waitKey(1) & 0xFF == ord('z'):
        break

cap.release()
cv2.destroyAllWindows()