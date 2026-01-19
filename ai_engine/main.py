import cv2
from ultralytics import YOLO
from gtts import gTTS
import pygame
import os
import time
import threading
import speech_recognition as sr
import smtplib
from email.message import EmailMessage

# =========================
# AUDIO INIT & LOCK
# =========================
pygame.mixer.init()
audio_lock = threading.Lock() # Taaki speak aur listen ek saath na ho

def speak(text):
    with audio_lock: # Jab tak bol raha hai, lock rahega
        try:
            filename = "voice.mp3"
            tts = gTTS(text=text, lang='en')
            tts.save(filename)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            pygame.mixer.music.unload()
            os.remove(filename)
        except:
            pass

# =========================
# EMAIL ALERT FUNCTION
# =========================
def send_emergency_email():
    try:
        SENDER_EMAIL = "your_email@gmail.com"
        SENDER_PASS = "your_app_password" # 16 digit code
        RECEIVER_EMAIL = "family@gmail.com"

        msg = EmailMessage()
        msg['Subject'] = "🚨 SMART SAHAYYAK: EMERGENCY ALERT"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg.set_content("The user needs help! This is an automated alert from Smart Sahayyak.")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("📧 Email Alert Sent!")
    except Exception as e:
        print(f"📧 Email Failed: {e}")

# =========================
# LOAD MODELS
# =========================
object_model = YOLO('yolov8n.pt')
try:
    currency_model = YOLO('models/currency_model.pt')
except:
    currency_model = None

# Global Flags
last_spoken = ""
blank_counter = 0
frame_count = 0

# =========================
# THREAD 1: VOICE LISTENER
# =========================
def voice_recognition_thread():
    recognizer = sr.Recognizer()
    while True:
        # Agar system khud bol raha hai, toh wait karo
        if audio_lock.locked():
            time.sleep(1)
            continue
            
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, phrase_time_limit=3)
                text = recognizer.recognize_google(audio).lower()
                print("Heard:", text)

                if "help" in text:
                    print("\n🚨 EMERGENCY TRIGGERED 🚨")
                    # Threading for email taaki camera na ruke
                    threading.Thread(target=send_emergency_email).start()
                    speak("Emergency alert sent to your family")
            except:
                pass

# =========================
# THREAD 2: CAMERA + AI
# =========================
def start_camera():
    global last_spoken, blank_counter, frame_count
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame_count += 1
        
        # Optimization
        if frame_count % 2 == 0:
            results = object_model(frame, conf=0.5, verbose=False)
            mode = "object"
        else:
            results = currency_model(frame, conf=0.6, verbose=False) if currency_model else object_model(frame, conf=0.5, verbose=False)
            mode = "currency" if currency_model else "object"

        if len(results[0].boxes) > 0:
            blank_counter = 0
            for box in results[0].boxes:
                label = results[0].names[int(box.cls[0])]
                message = f"I see {label}" if mode == "object" else f"{label} note"

                if message != last_spoken and not audio_lock.locked():
                    print(message)
                    threading.Thread(target=speak, args=(message,)).start()
                    last_spoken = message
        else:
            blank_counter += 1
            if blank_counter >= 100: # 3-4 seconds of silence
                if last_spoken != "blank" and not audio_lock.locked():
                    threading.Thread(target=speak, args=("Nothing detected",)).start()
                    last_spoken = "blank"
                blank_counter = 0

        cv2.imshow("Smart Sahayyak AI", results[0].plot())
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    t1 = threading.Thread(target=voice_recognition_thread, daemon=True)
    t1.start()
    start_camera()