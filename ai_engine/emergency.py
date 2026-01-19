import speech_recognition as sr
import requests
import webbrowser

# --- CONFIGURATION ---
# Filhal hum dummy message print karenge, 
# Real SMS ke liye Twilio use hota hai (wo hum Phase 2 mein karenge)
EMERGENCY_CONTACT = "+918160644058" 
KEYWORD = "help"

def get_location():
    """User ki current location nikalne ke liye"""
    try:
        # IP based location (Simple way for project)
        res = requests.get('https://ipapi.co/json/')
        data = res.json()
        location = f"City: {data['city']}, Region: {data['region']}, Lat/Lon: {data['latitude']},{data['longitude']}"
        maps_link = f"https://www.google.com/maps?q={data['latitude']},{data['longitude']}"
        return maps_link
    except:
        return "Location not found"

def trigger_emergency():
    print("\n🚨 EMERGENCY TRIGGERED! 🚨")
    location = get_location()
    message = f"I need help! My current location is: {location}"
    
    print(f"Sending message to {EMERGENCY_CONTACT}...")
    print(f"Content: {message}")
    
    # Testing ke liye browser mein location open kar dega
    webbrowser.open(location)

def listen_for_help():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print(f"\nListening for '{KEYWORD}' keyword...")
        recognizer.adjust_for_ambient_noise(source)
        
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=3)
                text = recognizer.recognize_google(audio).lower()
                print(f"You said: {text}")

                if KEYWORD in text:
                    trigger_emergency()
                    break # Ek baar trigger hone par stop (Testing ke liye)
            except sr.UnknownValueError:
                pass # Kuch samajh nahi aaya toh ignore
            except sr.RequestError:
                print("Internet connection error")

if __name__ == "__main__":
    listen_for_help()