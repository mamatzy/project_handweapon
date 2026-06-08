import pygame
import cv2
import numpy as np
import os
import random

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Street Racing - CV Controller")
clock = pygame.time.Clock()

path_file = os.path.dirname(os.path.abspath(__file__))
folder_asset = os.path.join(path_file, '..', 'assets')

def load_image(name, scale=None, rotate=0):
    path = os.path.join(folder_asset, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        if rotate != 0:
            img = pygame.transform.rotate(img, rotate)
        return img
    except FileNotFoundError:
        surface = pygame.Surface(scale if scale else (50, 30))
        surface.fill((255, 0, 0) if "car" in name else (100, 100, 100))
        return surface

bg_img = load_image('jalanan.png', scale=(SCREEN_HEIGHT, SCREEN_WIDTH), rotate=90)
bg_x1, bg_x2 = 0, SCREEN_WIDTH

player_size = (180, 150)
mobillain_size = (180, 150)
base_scale = (150, 180) 

player_img = load_image('car1.png', scale=base_scale, rotate=270)

obstacle_base_imgs = [
    load_image('car2.png', scale=base_scale, rotate=180), 
    load_image('car3.png', scale=base_scale),
    load_image('car4.png', scale=base_scale),
    load_image('car5.png', scale=base_scale, rotate=180),
    load_image('car6.png', scale=base_scale, rotate=90)
]

cap = cv2.VideoCapture(0)
current_state = "KOSONG"

player_x, player_y = 50, SCREEN_HEIGHT // 2
player_speed = 7

obstacles = []
score = 0
font = pygame.font.SysFont(None, 36)
running = True
game_over = False

spawn_timer = 0
lane_y_positions = [0, 150, 300, 450]

HITBOX_OFFSET_X = -40
HITBOX_OFFSET_Y = -60

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                game_over = False
                obstacles.clear()
                score = 0
                player_x, player_y = 50, SCREEN_HEIGHT // 2
                spawn_timer = 0
            if event.key == pygame.K_ESCAPE:
                running = False

    ret, frame = cap.read()
    if ret:
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
        lower1 = np.array([5, 80, 80], dtype=np.uint8)
        upper1 = np.array([40, 255, 255], dtype=np.uint8)
        maskCoklat = cv2.inRange(hsv, lower1, upper1)

        contours, _ = cv2.findContours(maskCoklat, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
                    
                    for name, (x1, y1, x2, y2) in zones.items():
                        if x1 <= cx <= x2 and y1 <= cy <= y2:
                            detected_zone = name
                            break

        if detected_zone != current_state:
            current_state = detected_zone

        cv2.putText(frame, f"STATUS: {current_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        mask_bgr = cv2.cvtColor(maskCoklat, cv2.COLOR_GRAY2BGR)
        frame_kecil = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        mask_kecil = cv2.resize(mask_bgr, (0, 0), fx=0.5, fy=0.5)
        debug_window = np.hstack((frame_kecil, mask_kecil))
        
        cv2.imshow("DEBUG OPENCV (DETEKSI & MASKING)", debug_window)
        cv2.waitKey(1) 

    if not game_over:
        if current_state == "W": player_y -= player_speed
        elif current_state == "S": player_y += player_speed
        elif current_state == "A": player_x -= player_speed
        elif current_state == "D": player_x += player_speed

        player_x = max(0, min(player_x, SCREEN_WIDTH // 2 - player_size[0]))
        player_y = max(0, min(player_y, SCREEN_HEIGHT - player_size[1]))
        
        player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])
        player_hitbox = player_rect.inflate(HITBOX_OFFSET_X, HITBOX_OFFSET_Y)

        bg_speed = 8
        bg_x1 -= bg_speed
        bg_x2 -= bg_speed
        if bg_x1 <= -SCREEN_WIDTH: bg_x1 = SCREEN_WIDTH
        if bg_x2 <= -SCREEN_WIDTH: bg_x2 = SCREEN_WIDTH

        if spawn_timer > 0:
            spawn_timer -= 1
        else:
            lane_index = random.randint(0, 3)
            obs_y = lane_y_positions[lane_index]
            
            jarak_aman_minimal = 350 
            aman_untuk_spawn = True
            
            for obs in obstacles:
                if obs['lane'] == lane_index and obs['rect'].x > (SCREEN_WIDTH - jarak_aman_minimal):
                    aman_untuk_spawn = False
                    break
            
            if aman_untuk_spawn:
                base_img = random.choice(obstacle_base_imgs)
                
                if lane_index < 2:
                    obs_img = pygame.transform.rotate(base_img, 90)
                    obs_speed = -16
                else:
                    obs_img = pygame.transform.rotate(base_img, 270)
                    obs_speed = -4
                    
                obstacles.append({
                    'rect': pygame.Rect(SCREEN_WIDTH, obs_y, mobillain_size[0], mobillain_size[1]), 
                    'img': obs_img, 
                    'speed': obs_speed,
                    'lane': lane_index
                })
                
                spawn_timer = random.randint(20, 40)

        for obs in obstacles[:]:
            obs['rect'].x += obs['speed']
            
            if obs['rect'].x < -mobillain_size[0]:
                obstacles.remove(obs)
                score += 10
            
            obs_hitbox = obs['rect'].inflate(HITBOX_OFFSET_X, HITBOX_OFFSET_Y)
            
            if player_hitbox.colliderect(obs_hitbox):
                game_over = True

    screen.blit(bg_img, (bg_x1, 0))
    screen.blit(bg_img, (bg_x2, 0))

    if not game_over:
        screen.blit(player_img, (player_rect.x, player_rect.y))
        for obs in obstacles:
            screen.blit(obs['img'], (obs['rect'].x, obs['rect'].y))
            
        score_text = font.render(f"Skor: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
    else:
        go_text = font.render(f"GAME OVER! Skor: {score}", True, (255, 50, 50))
        retry_text = font.render("Tekan 'R' untuk ulang, 'ESC' untuk keluar", True, (255, 255, 255))
        screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(retry_text, (SCREEN_WIDTH//2 - retry_text.get_width()//2, SCREEN_HEIGHT//2 + 10))

    pygame.display.flip()
    clock.tick(60)

cap.release()
cv2.destroyAllWindows()
pygame.quit()