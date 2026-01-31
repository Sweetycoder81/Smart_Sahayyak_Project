"""
Hearing Module for TriSense AI
Speech-to-text conversion for deaf users using SpeechRecognition
"""

import speech_recognition as sr
import threading
import time
import sys
import os
from typing import Optional, List, Dict
from datetime import datetime
import queue

from utils.logger import LoggerMixin, log_exception
from config.settings import Config


class HearingDisplay:
    """Display handler for large text output"""
    
    def __init__(self):
        self.transcripts = []  # Store recent transcripts
        self.max_lines = 10
        self.listening = False
        self.animation_frame = 0
    
    def add_transcript(self, text: str):
        """Add a new transcript to display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transcripts.append({
            'text': text,
            'timestamp': timestamp
        })
        
        # Keep only recent transcripts
        if len(self.transcripts) > self.max_lines:
            self.transcripts.pop(0)
    
    def clear_display(self):
        """Clear the display"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_listening_animation(self) -> str:
        """Get animated listening indicator"""
        animations = ["⏺", "⏺⏺", "⏺⏺⏺", "⏺⏺", "⏺"]
        self.animation_frame = (self.animation_frame + 1) % len(animations)
        return animations[self.animation_frame]
    
    def display_console(self):
        """Display transcripts in console with large fonts"""
        self.clear_display()
        
        # Header
        print("=" * 80)
        print("🎤 TRISENSE AI - HEARING MODULE".center(80))
        print("=" * 80)
        
        # Listening status
        if self.listening:
            listening_text = f"🔴 LISTENING {self.get_listening_animation()}"
            print(f"\n{listening_text:^80}")
        else:
            print(f"\n{'⏸ PAUSED':^80}")
        
        print("\n" + "─" * 80)
        
        # Display transcripts with large font effect
        if self.transcripts:
            print("📝 RECENT TRANSCRIPTS:")
            print("─" * 80)
            
            for i, transcript in enumerate(self.transcripts[-self.max_lines:], 1):
                # Large font effect using multiple lines
                text = transcript['text'].upper()
                timestamp = transcript['timestamp']
                
                print(f"\n[{timestamp}] {i}.")
                print("┌" + "─" * (len(text) + 4) + "┐")
                print(f"│  {text:^{len(text)}}  │")
                print("└" + "─" * (len(text) + 4) + "┘")
        else:
            print("\n" + "🔇 NO SPEECH DETECTED YET".center(80))
            print("Start speaking to see transcripts here...".center(80))
        
        print("\n" + "─" * 80)
        print("💡 CONTROLS: Press Ctrl+C to stop listening".center(80))
        print("=" * 80)
    
    def display_popup_info(self):
        """Display information about popup window (placeholder)"""
        print("\n📺 POPUP WINDOW: Large text display would appear here")
        print("   (Terminal mode active - showing large text above)")


class LanguageConfig:
    """Language configuration for speech recognition"""
    
    LANGUAGES = {
        'english': {
            'code': 'en-US',
            'name': 'English',
            'display_name': 'ENGLISH'
        },
        'hindi': {
            'code': 'hi-IN',
            'name': 'Hindi',
            'display_name': 'हिंदी'
        },
        'gujarati': {
            'code': 'gu-IN',
            'name': 'Gujarati',
            'display_name': 'ગુજરાતી'
        }
    }
    
    @classmethod
    def get_language_config(cls, language: str) -> Dict:
        """Get language configuration"""
        return cls.LANGUAGES.get(language.lower(), cls.LANGUAGES['english'])
    
    @classmethod
    def get_available_languages(cls) -> List[str]:
        """Get list of available languages"""
        return list(cls.LANGUAGES.keys())


class HearingModule(LoggerMixin):
    """Hearing Module for continuous speech recognition"""
    
    def __init__(self, language: str = 'english'):
        """Initialize Hearing Module"""
        super().__init__()
        self.config = Config.get_config('hearing')
        self.language_config = LanguageConfig.get_language_config(language)
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        
        # Threading
        self.running = False
        self.listening_thread: Optional[threading.Thread] = None
        self.display_thread: Optional[threading.Thread] = None
        
        # Display
        self.display = HearingDisplay()
        
        # Audio settings
        self.energy_threshold = self.config.get('energy_threshold', 300)
        self.phrase_time_limit = self.config.get('phrase_time_limit', 5)
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.chunk_size = self.config.get('chunk_size', 1024)
        
        # Statistics
        self.recognition_count = 0
        self.error_count = 0
        self.start_time = None
        
        # Queue for thread-safe communication
        self.transcript_queue = queue.Queue()
        
        self.logger.info(f"Hearing Module initialized for {self.language_config['name']}")
    
    def initialize_microphone(self) -> bool:
        """
        Initialize microphone for speech recognition
        
        Returns:
            True if microphone initialized successfully, False otherwise
        """
        try:
            # Get microphone index if specified
            mic_index = self.config.get('microphone_index')
            
            if mic_index is not None:
                self.microphone = sr.Microphone(device_index=mic_index)
                self.logger.info(f"Using microphone at index: {mic_index}")
            else:
                self.microphone = sr.Microphone()
                self.logger.info("Using default microphone")
            
            # Test microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Configure recognizer
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            self.logger.info("Microphone initialized successfully")
            return True
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to initialize microphone")
            return False
    
    def recognize_speech(self, audio_data) -> Optional[str]:
        """
        Recognize speech from audio data
        
        Args:
            audio_data: Audio data from microphone
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            # Use Google Web Speech API
            text = self.recognizer.recognize_google(
                audio_data,
                language=self.language_config['code'],
                show_all=False
            )
            
            self.recognition_count += 1
            self.logger.info(f"Recognized: {text}")
            return text
            
        except sr.UnknownValueError:
            # Speech was not understood
            self.logger.debug("Speech not understood")
            return None
            
        except sr.RequestError as e:
            # API error
            self.logger.error(f"Google Speech API error: {e}")
            self.error_count += 1
            return None
            
        except Exception as e:
            log_exception(self.logger, e, "Speech recognition error")
            self.error_count += 1
            return None
    
    def listening_loop(self):
        """Main listening loop running in separate thread"""
        self.logger.info("Starting listening loop")
        
        with self.microphone as source:
            # Adjust for ambient noise
            if self.config.get('adjust_for_ambient_noise', True):
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        while self.running:
            try:
                self.display.listening = True
                
                # Listen for audio
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(
                            source,
                            timeout=1,
                            phrase_time_limit=self.phrase_time_limit
                        )
                    except sr.WaitTimeoutError:
                        # No speech detected within timeout
                        continue
                
                self.display.listening = False
                
                # Recognize speech
                text = self.recognize_speech(audio)
                
                if text and text.strip():
                    # Add to display queue
                    self.transcript_queue.put(text)
                    self.logger.info(f"Speech detected: {text}")
                
            except Exception as e:
                log_exception(self.logger, e, "Error in listening loop")
                time.sleep(0.1)
        
        self.logger.info("Listening loop ended")
    
    def display_loop(self):
        """Display loop for updating console output"""
        self.logger.info("Starting display loop")
        
        while self.running:
            try:
                # Check for new transcripts
                try:
                    while True:
                        text = self.transcript_queue.get_nowait()
                        self.display.add_transcript(text)
                except queue.Empty:
                    pass
                
                # Update display
                self.display.display_console()
                
                # Small delay to prevent flickering
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                log_exception(self.logger, e, "Error in display loop")
                time.sleep(0.5)
        
        self.logger.info("Display loop ended")
    
    def start(self) -> bool:
        """
        Start the Hearing Module
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting Hearing Module")
            
            # Initialize microphone
            if not self.initialize_microphone():
                self.logger.error("Failed to initialize microphone")
                return False
            
            # Start timing
            self.start_time = time.time()
            
            # Start threads
            self.running = True
            
            # Start listening thread
            self.listening_thread = threading.Thread(target=self.listening_loop, daemon=True)
            self.listening_thread.start()
            
            # Start display thread
            self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
            self.display_thread.start()
            
            self.logger.info("Hearing Module started successfully")
            return True
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to start Hearing Module")
            return False
    
    def stop(self):
        """Stop the Hearing Module"""
        try:
            self.logger.info("Stopping Hearing Module")
            
            # Stop running
            self.running = False
            self.display.listening = False
            
            # Wait for threads to finish
            if self.listening_thread and self.listening_thread.is_alive():
                self.listening_thread.join(timeout=2.0)
            
            if self.display_thread and self.display_thread.is_alive():
                self.display_thread.join(timeout=1.0)
            
            # Clear display
            self.display.clear_display()
            
            # Log statistics
            if self.start_time:
                duration = time.time() - self.start_time
                self.logger.info(f"Hearing Module stopped. Stats: "
                               f"Duration: {duration:.1f}s, "
                               f"Recognitions: {self.recognition_count}, "
                               f"Errors: {self.error_count}")
            
        except Exception as e:
            log_exception(self.logger, e, "Error stopping Hearing Module")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current status of Hearing Module
        
        Returns:
            Dictionary containing status information
        """
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'running': self.running,
            'listening': self.display.listening,
            'language': self.language_config['name'],
            'recognition_count': self.recognition_count,
            'error_count': self.error_count,
            'duration': duration,
            'transcript_count': len(self.display.transcripts),
            'energy_threshold': self.recognizer.energy_threshold if self.recognizer else 0
        }
    
    def set_language(self, language: str) -> bool:
        """
        Change recognition language
        
        Args:
            language: Language name ('english', 'hindi', 'gujarati')
            
        Returns:
            True if language changed successfully, False otherwise
        """
        try:
            new_config = LanguageConfig.get_language_config(language)
            self.language_config = new_config
            self.logger.info(f"Language changed to {new_config['name']}")
            return True
        except Exception as e:
            log_exception(self.logger, e, f"Failed to change language to {language}")
            return False
    
    def adjust_microphone(self):
        """Adjust microphone for ambient noise"""
        try:
            if self.microphone:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.logger.info("Microphone adjusted for ambient noise")
        except Exception as e:
            log_exception(self.logger, e, "Failed to adjust microphone")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return LanguageConfig.get_available_languages()
    
    def clear_transcripts(self):
        """Clear all transcripts"""
        self.display.transcripts.clear()
        self.logger.info("Transcripts cleared")
