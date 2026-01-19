import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import os

# Warnings off
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()
cap = cv2.VideoCapture(0)

# Settings
# Isse thoda kam rakha hai taaki box bada dikhe
frame_reduction = 70  
smoothing = 5
plocX, plocY = 0, 0

print("Gesture Navigation PRO (Visible Box) is active...")

while True:
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # --- VISUAL BOX ---
    # Is rectangle ke andar hi tumhara haath move hona chahiye
    cv2.rectangle(frame, (frame_reduction, frame_reduction), 
                  (w - frame_reduction, h - frame_reduction), (255, 0, 255), 3)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Index tip (8) and Thumb tip (4)
            points = hand_landmarks.landmark
            itip = points[8]
            ttip = points[4]

            # X and Y coordinates in pixels
            ix, iy = int(itip.x * w), int(itip.y * h)

            # --- LOGIC: Check if hand is INSIDE the box ---
            if frame_reduction < ix < w - frame_reduction and frame_reduction < iy < h - frame_reduction:
                
                # Mapping coordinates
                x3 = np.interp(ix, (frame_reduction, w - frame_reduction), (0, screen_width))
                y3 = np.interp(iy, (frame_reduction, h - frame_reduction), (0, screen_height))

                # Smoothing
                clocX = plocX + (x3 - plocX) / smoothing
                clocY = plocY + (y3 - plocY) / smoothing
                
                try:
                    pyautogui.moveTo(clocX, clocY, _pause=False)
                except:
                    pass
                
                plocX, plocY = clocX, clocY

                # Click logic
                dist = np.hypot(itip.x - ttip.x, itip.y - ttip.y)
                if dist < 0.04:
                    cv2.circle(frame, (ix, iy), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()
            else:
                # Agar haath box ke bahar hai toh border red ho jayega (Warning)
                cv2.rectangle(frame, (frame_reduction, frame_reduction), 
                              (w - frame_reduction, h - frame_reduction), (0, 0, 255), 3)

    cv2.imshow("Gesture Control (Stay inside the Pink Box)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()