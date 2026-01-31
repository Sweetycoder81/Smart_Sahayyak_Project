"""
Text-to-Speech Engine for TriSense AI
Centralized TTS functionality using pyttsx3 for offline capability
"""

import pyttsx3
import threading
import time
from typing import Optional

class TTSEngine:
    """Thread-safe Text-to-Speech engine using pyttsx3"""
    
    def __init__(self, rate: int = 150, volume: float = 0.9):
        """
        Initialize TTS Engine
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.engine = pyttsx3.init()
        self.rate = rate
        self.volume = volume
        self.audio_lock = threading.Lock()
        self.is_speaking = False
        
        # Configure voice properties
        self._configure_voice()
    
    def _configure_voice(self):
        """Configure voice properties"""
        try:
            # Set speech rate
            self.engine.setProperty('rate', self.rate)
            
            # Set volume
            self.engine.setProperty('volume', self.volume)
            
            # Try to set a female voice if available
            voices = self.engine.getProperty('voices')
            for voice in voices:
                # Note: pyttsx3 Voice objects don't have 'lang' attribute consistently
                # We'll check voice name instead
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"Warning: Could not configure voice properties: {e}")
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            blocking: Whether to wait for speech to complete
            
        Returns:
            bool: True if speech started successfully
        """
        if not text or not text.strip():
            return False
        
        def _speak_thread():
            try:
                with self.audio_lock:
                    self.is_speaking = True
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.is_speaking = False
            except Exception as e:
                print(f"TTS Error: {e}")
                self.is_speaking = False
        
        if blocking:
            _speak_thread()
        else:
            thread = threading.Thread(target=_speak_thread, daemon=True)
            thread.start()
        
        return True
    
    def stop(self):
        """Stop current speech"""
        try:
            with self.audio_lock:
                self.engine.stop()
                self.is_speaking = False
        except Exception as e:
            print(f"Error stopping TTS: {e}")
    
    def is_busy(self) -> bool:
        """Check if TTS is currently speaking"""
        return self.is_speaking or self.audio_lock.locked()
    
    def list_voices(self):
        """List available voices"""
        try:
            voices = self.engine.getProperty('voices')
            for i, voice in enumerate(voices):
                print(f"{i}: {voice.name} ({voice.lang})")
        except Exception as e:
            print(f"Error listing voices: {e}")
    
    def set_voice(self, voice_id: str):
        """Set voice by ID"""
        try:
            self.engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            print(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: int):
        """Set speech rate"""
        try:
            self.engine.setProperty('rate', rate)
            self.rate = rate
            return True
        except Exception as e:
            print(f"Error setting rate: {e}")
            return False
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        try:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            self.volume = volume
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False

# Global TTS instance
_tts_instance: Optional[TTSEngine] = None

def get_tts_engine() -> TTSEngine:
    """Get or create global TTS engine instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSEngine()
    return _tts_instance

def speak(text: str, blocking: bool = False) -> bool:
    """Convenience function to speak text"""
    return get_tts_engine().speak(text, blocking)
