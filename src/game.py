import cv2
import numpy as np
import os
import random
import time

def overlay_transparent(bg, overlay, x, y):
    h, w = overlay.shape[:2]
    y1, y2 = max(0, int(y)), min(bg.shape[0], int(y) + h)
    x1, x2 = max(0, int(x)), min(bg.shape[1], int(x) + w)
    oy1, oy2 = max(0, -int(y)), min(h, h - ((int(y) + h) - bg.shape[0]))
    ox1, ox2 = max(0, -int(x)), min(w, w - ((int(x) + w) - bg.shape[1]))
    
    if y1 >= y2 or x1 >= x2:
        return bg

    bg_crop = bg[y1:y2, x1:x2]
    overlay_crop = overlay[oy1:oy2, ox1:ox2]
    
    alpha = np.expand_dims(overlay_crop[:, :, 3] / 255.0, axis=2)
    blended = (1.0 - alpha) * bg_crop + alpha * overlay_crop[:, :, :3]
    bg[y1:y2, x1:x2] = blended.astype(np.uint8)
    return bg

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LOWER_SKIN = np.array([0, 40, 80])
UPPER_SKIN = np.array([20, 255, 255])

path_file = os.path.dirname(os.path.abspath(__file__))
folder_asset = os.path.join(path_file, '..', 'assets')

def load_cv_image(name, dsize=None, rotate=None):
    path = os.path.join(folder_asset, name)
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        img = np.zeros((100, 100, 4), dtype=np.uint8)
        img[:,:] = (0, 0, 255, 255)
    else:
        if dsize: img = cv2.resize(img, dsize)
        if rotate is not None: img = cv2.rotate(img, rotate)
    return img

# ========================================================
# BLOK KONFIGURASI ASET FIX (TIDAK DIUBAH)
# ========================================================
bg_img = cv2.imread(os.path.join(folder_asset, 'jalanan.png'))
if bg_img is not None:
    bg_img = cv2.rotate(bg_img, cv2.ROTATE_90_CLOCKWISE)
    bg_img = cv2.resize(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    bg_img = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)

base_scale = (150, 180) 
player_img = load_cv_image('car1.png', dsize=base_scale)
player_img = cv2.rotate(player_img, cv2.ROTATE_90_CLOCKWISE)

obstacle_base_imgs = [
    load_cv_image('car2.png', dsize=base_scale, rotate=cv2.ROTATE_90_COUNTERCLOCKWISE),
    load_cv_image('car3.png', dsize=base_scale, rotate=cv2.ROTATE_90_CLOCKWISE),
    load_cv_image('car4.png', dsize=base_scale, rotate=cv2.ROTATE_90_CLOCKWISE),
    load_cv_image('car5.png', dsize=base_scale, rotate=cv2.ROTATE_90_COUNTERCLOCKWISE),
    load_cv_image('car6.png', dsize=base_scale),
]
# ========================================================

cap = cv2.VideoCapture(0)

current_state = "KOSONG"
gesture_state = "HOVER"
bg_x = 0
score = 0
obstacles = []
spawn_timer = 0
lane_y_positions = [20, 160, 310, 450]
game_over = False

player_x, player_y = 50.0, SCREEN_HEIGHT // 2
player_speed = 7
base_bg_speed = 8
extra_world_speed = 0
target_player_x = 50
HITBOX_W, HITBOX_H = 160, 120

kernel = np.ones((5, 5), np.uint8)

boost_end_time = 0
cooldown_end_time = 0
is_boosting = False

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    h_frame, w_frame = frame.shape[:2]
    w_half, h_half = w_frame // 2, h_frame // 2
    w_step, h_step = w_half // 3, h_half // 2
    
    zones = {
        "W": (w_step, h_half, w_step * 2, h_half + h_step),
        "A": (0, h_half + h_step, w_step, h_frame),
        "S": (w_step, h_half + h_step, w_step * 2, h_frame),
        "D": (w_step * 2, h_half + h_step, w_half, h_frame),
        "MOUSE": (w_half, h_half, w_frame, h_frame)
    }

    for name, (x1, y1, x2, y2) in zones.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, name, (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_zone = "KOSONG"
    gesture_state = "HOVER"
    
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) > 3000:
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                for name, (zx1, zy1, zx2, zy2) in zones.items():
                    if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                        detected_zone = name
                        break
                        
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            hull = cv2.convexHull(max_contour, returnPoints=False)
            if hull is not None and len(hull) > 3 and len(max_contour) > 3:
                try:
                    defects = cv2.convexityDefects(max_contour, hull)
                    finger_count = 0
                    if defects is not None:
                        for i in range(defects.shape[0]):
                            s, e, f, d = defects[i, 0]
                            if d > 12000:
                                finger_count += 1
                                
                    if finger_count <= 1:
                        gesture_state = "ATTACK"
                except: pass

            cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)

    if detected_zone != current_state:
        current_state = detected_zone

    current_time = time.time()
    
    # Logika Boost yang Anti-Flicker
    if gesture_state == "ATTACK" and current_time > cooldown_end_time and not is_boosting:
        is_boosting = True
        boost_end_time = current_time + 3.0

    if is_boosting and current_time > boost_end_time:
        is_boosting = False
        cooldown_end_time = current_time + 5.0
        
    is_cooldown = (not is_boosting) and (current_time < cooldown_end_time)

    cv2.putText(frame, f"ZONE: {current_state} | GESTURE: {gesture_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    canvas = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
    
    if not game_over:
        extra_world_speed = 0
        target_player_x = 50

        # Konfigurasi WASD Sesuai Permintaan
        if current_state == "D":
            extra_world_speed = 12
            target_player_x = 150
        elif current_state == "A":
            extra_world_speed = -5
            target_player_x = 20
        elif current_state == "W":
            player_y -= player_speed
        elif current_state == "S":
            player_y += player_speed

        player_x += (target_player_x - player_x) * 0.1
        player_y = max(0, min(player_y, SCREEN_HEIGHT - 150))
        
        current_bg_speed = base_bg_speed + extra_world_speed
        bg_x = (bg_x + current_bg_speed) % SCREEN_WIDTH
    
    canvas[:, :SCREEN_WIDTH-int(bg_x)] = bg_img[:, int(bg_x):]
    canvas[:, SCREEN_WIDTH-int(bg_x):] = bg_img[:, :int(bg_x)]

    if not game_over:
        if spawn_timer > 0:
            spawn_timer -= 1
        else:
            lane_idx = random.randint(0, 3)
            lane_y = lane_y_positions[lane_idx]
            
            safe = True
            for obs in obstacles:
                if obs['lane'] == lane_idx and obs['x'] > SCREEN_WIDTH - 350:
                    safe = False
                    break
            
            if safe:
                base_img = random.choice(obstacle_base_imgs)
                if lane_idx < 2:
                    # Lane Berlawanan: Balik arah (Flip 180 Derajat) dan laju cepat
                    obs_img = cv2.rotate(base_img, cv2.ROTATE_180)
                    obs_base_speed = random.randint(14, 20)
                else:
                    # Lane Searah: Tanpa rotasi dan laju pelan
                    obs_img = base_img
                    obs_base_speed = random.randint(3, 7)
                    
                obstacles.append({
                    'x': SCREEN_WIDTH, 'y': lane_y, 
                    'img': obs_img, 'base_speed': obs_base_speed,
                    'lane': lane_idx
                })
                spawn_timer = random.randint(20, 40)

        player_box = [player_x + 20, player_y + 30, player_x + HITBOX_W, player_y + HITBOX_H]

        for obs in obstacles[:]:
            actual_speed = obs['base_speed'] + extra_world_speed
            obs['x'] -= actual_speed
            
            if obs['x'] < -200 or obs['x'] > SCREEN_WIDTH + 200:
                obstacles.remove(obs)
                if obs['x'] < -200:
                    score += 5
                continue
                
            obs_box = [obs['x'] + 20, obs['y'] + 30, obs['x'] + HITBOX_W, obs['y'] + HITBOX_H]
            
            collide = (player_box[0] < obs_box[2] and player_box[2] > obs_box[0] and
                       player_box[1] < obs_box[3] and player_box[3] > obs_box[1])
            
            if collide:
                if is_boosting:
                    obstacles.remove(obs)
                    score += 20
                else:
                    game_over = True

    for obs in obstacles:
        canvas = overlay_transparent(canvas, obs['img'], obs['x'], obs['y'])

    if not game_over:
        canvas = overlay_transparent(canvas, player_img, player_x, player_y)
        
        cv2.putText(canvas, f"GESTURE: {gesture_state}", (SCREEN_WIDTH - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if gesture_state == "HOVER" else (0, 0, 255), 2)
        
        if is_boosting:
            rem = max(0.0, round(boost_end_time - current_time, 1))
            cv2.putText(canvas, f"BOOST! {rem}s", (int(player_x), int(player_y)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 3)
        elif is_cooldown:
            rem = max(0.0, round(cooldown_end_time - current_time, 1))
            cv2.putText(canvas, f"COOLDOWN! {rem}s", (int(player_x), int(player_y)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
    else:
        cv2.putText(canvas, "CRASHED! TEKAN 'R' UNTUK RESTART", (100, SCREEN_HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            game_over = False
            obstacles.clear()
            score = 0
            is_boosting = False
            boost_end_time = 0
            cooldown_end_time = 0

    cv2.putText(canvas, f"SCORE: {score}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    frame_kecil = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    mask_kecil = cv2.resize(mask_bgr, (0, 0), fx=0.5, fy=0.5)
    debug_window = np.hstack((frame_kecil, mask_kecil))
    
    cv2.imshow("Debug View (Camera & Mask)", debug_window)
    cv2.imshow("Main Game (Pure OpenCV)", canvas)

    if cv2.waitKey(1) & 0xFF == ord('z'):
        break

cap.release()
cv2.destroyAllWindows()