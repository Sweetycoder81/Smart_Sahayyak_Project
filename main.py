"""
TriSense AI - Multi-modal Assistive Intelligence System
Main Controller with CLI Interface for switching between disability modules
"""

import sys
import os
import time
import threading
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.tts_engine import get_tts_engine
from utils.logger import setup_logger, get_logger

# Import modules
from modules.vision_module import VisionModule
from modules.hearing_module import HearingModule
from modules.voice_module import VoiceModule

class TriSenseController:
    """Main controller for TriSense AI system"""
    
    def __init__(self):
        self.logger = setup_logger("TriSense")
        self.tts_engine = get_tts_engine()
        self.current_module = None
        self.running = False
        
        # Module instances
        self.vision_module = None
        self.hearing_module = None
        self.voice_module = None
        
        self.logger.info("TriSense AI Controller initialized")
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                    TriSense AI - Assistive Intelligence       ║
║                                                              ║
║  Multi-modal system for:                                     ║
║  • Vision Assistance (For the Blind)                        ║
║  • Hearing Assistance (For the Deaf)                        ║
║  • Voice Assistance (For the Mute)                           ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(welcome_text)
        self.tts_engine.speak("Welcome to TriSense AI Assistive System")
    
    def display_menu(self):
        """Display main menu"""
        menu_text = """
╔══════════════════════════════════════════════════════════════╗
║                        MAIN MENU                             ║
╠══════════════════════════════════════════════════════════════╣
║  1. Vision Module    - Object detection for blind users       ║
║  2. Hearing Module   - Speech-to-text for deaf users         ║
║  3. Voice Module     - Text-to-speech for mute users         ║
║  4. Settings         - Configure system settings             ║
║  5. Test System      - Test all modules                      ║
║  6. Help             - Display help information              ║
║  0. Exit             - Exit TriSense AI                      ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(menu_text)
    
    def get_user_choice(self) -> str:
        """Get user menu choice"""
        try:
            choice = input("\nEnter your choice (0-6): ").strip()
            return choice
        except KeyboardInterrupt:
            return "0"
        except EOFError:
            return "0"
    
    def handle_vision_module(self):
        """Handle Vision Module selection"""
        print("\n🔍 Starting Vision Module...")
        self.tts_engine.speak("Starting Vision Module for blind users")
        
        try:
            # Initialize Vision Module
            self.vision_module = VisionModule()
            
            print("Initializing camera and AI model...")
            if not self.vision_module.start():
                print("❌ Failed to start Vision Module")
                self.tts_engine.speak("Failed to start Vision Module")
                input("Press Enter to continue...")
                return
            
            print("✅ Vision Module started successfully!")
            print("📹 Camera is active and detecting objects...")
            print("🎯 Objects will be announced via voice")
            print("\nControls:")
            print("  • Press 'q' in the camera window to quit")
            print("  • Press 'c' in the camera window to clear cooldown timers")
            print("  • Close this window to stop the module")
            
            # Wait for user to stop the module
            while self.vision_module.running:
                time.sleep(0.5)
                
                # Check if user wants to stop
                if not self.vision_module.running:
                    break
            
            # Stop the module
            self.vision_module.stop()
            print("Vision Module stopped.")
            
        except KeyboardInterrupt:
            print("\nStopping Vision Module...")
            if self.vision_module:
                self.vision_module.stop()
        except Exception as e:
            self.logger.error(f"Vision Module error: {e}")
            print(f"Error starting Vision Module: {e}")
            self.tts_engine.speak("Error starting Vision Module")
            if self.vision_module:
                self.vision_module.stop()
            input("Press Enter to continue...")
    
    def handle_hearing_module(self):
        """Handle Hearing Module selection"""
        print("\n👂 Starting Hearing Module...")
        self.tts_engine.speak("Starting Hearing Module for deaf users")
        
        try:
            # Initialize Hearing Module
            self.hearing_module = HearingModule()
            
            print("Initializing microphone and speech recognition...")
            if not self.hearing_module.start():
                print("❌ Failed to start Hearing Module")
                self.tts_engine.speak("Failed to start Hearing Module")
                input("Press Enter to continue...")
                return
            
            print("✅ Hearing Module started successfully!")
            print("🎤 Microphone is active and listening...")
            print("📝 Speech will be displayed in LARGE text")
            print("\n🌍 Available Languages:")
            for lang in self.hearing_module.get_available_languages():
                print(f"  • {lang.title()}")
            
            print("\nControls:")
            print("  • Speak clearly into the microphone")
            print("  • Press Ctrl+C to stop listening")
            print("  • Close this window to stop the module")
            
            try:
                # Wait for user to stop the module
                while self.hearing_module.running:
                    time.sleep(0.5)
                    
                    # Check if module is still running
                    if not self.hearing_module.running:
                        break
                        
            except KeyboardInterrupt:
                print("\nStopping Hearing Module...")
            
            # Stop the module
            self.hearing_module.stop()
            print("Hearing Module stopped.")
            
        except KeyboardInterrupt:
            print("\nStopping Hearing Module...")
            if self.hearing_module:
                self.hearing_module.stop()
        except Exception as e:
            self.logger.error(f"Hearing Module error: {e}")
            print(f"Error starting Hearing Module: {e}")
            self.tts_engine.speak("Error starting Hearing Module")
            if self.hearing_module:
                self.hearing_module.stop()
            input("Press Enter to continue...")
    
    def handle_voice_module(self):
        """Handle Voice Module selection"""
        print("\n🗣️  Starting Voice Module...")
        self.tts_engine.speak("Starting Voice Module for mute users")
        
        try:
            # Initialize Voice Module
            self.voice_module = VoiceModule()
            
            print("Initializing text-to-speech engine...")
            if not self.voice_module.start():
                print("❌ Failed to start Voice Module")
                self.tts_engine.speak("Failed to start Voice Module")
                input("Press Enter to continue...")
                return
            
            print("✅ Voice Module started successfully!")
            print("📝 Chat interface is ready...")
            print("🎯 Your typed messages will be spoken instantly")
            print("⚡ Quick phrases available for instant communication")
            
            # Module runs its own interface loop
            # The start() method handles the user interaction
            
            # Stop the module
            self.voice_module.stop()
            print("Voice Module stopped.")
            
        except KeyboardInterrupt:
            print("\nStopping Voice Module...")
            if self.voice_module:
                self.voice_module.stop()
        except Exception as e:
            self.logger.error(f"Voice Module error: {e}")
            print(f"Error starting Voice Module: {e}")
            self.tts_engine.speak("Error starting Voice Module")
            if self.voice_module:
                self.voice_module.stop()
            input("Press Enter to continue...")
    
    def handle_settings(self):
        """Handle Settings menu"""
        print("\n⚙️  System Settings")
        self.tts_engine.speak("Opening system settings")
        
        while True:
            settings_menu = """
╔══════════════════════════════════════════════════════════════╗
║                        SETTINGS                              ║
╠══════════════════════════════════════════════════════════════╣
║  1. Voice Settings   - Configure TTS voice and speed         ║
║  2. Test Audio       - Test text-to-speech functionality    ║
║  3. System Info      - Display system information           ║
║  0. Back to Menu     - Return to main menu                   ║
╚══════════════════════════════════════════════════════════════╝
            """
            print(settings_menu)
            
            choice = input("Enter your choice (0-3): ").strip()
            
            if choice == "1":
                self.handle_voice_settings()
            elif choice == "2":
                self.test_audio()
            elif choice == "3":
                self.display_system_info()
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")
                self.tts_engine.speak("Invalid choice")
    
    def handle_voice_settings(self):
        """Handle voice settings configuration"""
        print("\n🎤 Voice Settings")
        
        try:
            print("Available voices:")
            self.tts_engine.list_voices()
            
            rate = input(f"Enter speech rate (current: {self.tts_engine.rate}): ").strip()
            if rate.isdigit():
                self.tts_engine.set_rate(int(rate))
                print(f"Speech rate set to {rate}")
            
            volume = input(f"Enter volume 0.0-1.0 (current: {self.tts_engine.volume}): ").strip()
            try:
                vol = float(volume)
                if 0.0 <= vol <= 1.0:
                    self.tts_engine.set_volume(vol)
                    print(f"Volume set to {vol}")
            except ValueError:
                pass
            
            self.tts_engine.speak("Voice settings updated")
            
        except Exception as e:
            self.logger.error(f"Voice settings error: {e}")
            print(f"Error updating settings: {e}")
        
        input("\nPress Enter to continue...")
    
    def test_audio(self):
        """Test audio functionality"""
        print("\n🔊 Testing Audio System")
        test_text = "Hello, this is a test of the TriSense AI audio system."
        
        print(f"Testing: {test_text}")
        self.tts_engine.speak(test_text, blocking=True)
        
        input("\nPress Enter to continue...")
    
    def display_system_info(self):
        """Display system information"""
        print("\n📋 System Information")
        print(f"Python Version: {sys.version}")
        print(f"Platform: {sys.platform}")
        print(f"TTS Engine: pyttsx3")
        print("Modules Status: Pending implementation")
        
        input("\nPress Enter to continue...")
    
    def handle_test_system(self):
        """Handle system testing"""
        print("\n🧪 Testing TriSense AI System")
        self.tts_engine.speak("Running system diagnostics")
        
        # Test TTS
        print("Testing Text-to-Speech...")
        if self.tts_engine.speak("TTS test successful"):
            print("✅ TTS System: OK")
        else:
            print("❌ TTS System: FAILED")
        
        # Test modules (placeholder)
        print("Testing Module Imports...")
        try:
            # TODO: Test actual module imports
            print("✅ Module Structure: OK (modules not yet implemented)")
        except Exception as e:
            print(f"❌ Module Structure: FAILED - {e}")
        
        print("\nSystem test completed.")
        self.tts_engine.speak("System test completed")
        
        input("\nPress Enter to continue...")
    
    def handle_help(self):
        """Display help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                           HELP                                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  TriSense AI provides three main modules:                    ║
║                                                              ║
║  🔍 VISION MODULE:                                           ║
║     - Real-time object detection using camera                ║
║     - Voice announcements of detected objects               ║
║     - Cool-down timer to prevent repetition                 ║
║                                                              ║
║  👂 HEARING MODULE:                                          ║
║     - Continuous speech recognition from microphone          ║
║     - Real-time text display of spoken words                ║
║     - Large font display for easy reading                   ║
║                                                              ║
║  🗣️  VOICE MODULE:                                           ║
║     - Text-to-speech proxy for communication                ║
║     - Type text and press Enter to speak                    ║
║     - Natural voice output                                   ║
║                                                              ║
║  CONTROLS:                                                   ║
║  - Use number keys to select menu options                    ║
║  - Press Ctrl+C to exit any module                           ║
║  - Press Enter to confirm selections                         ║
║                                                              ║
║  REQUIREMENTS:                                               ║
║  - Camera for Vision Module                                  ║
║  - Microphone for Hearing Module                             ║
║  - Speakers for audio output                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(help_text)
        self.tts_engine.speak("Help menu opened. Use arrow keys to scroll if needed.")
        input("\nPress Enter to return to main menu...")
    
    def cleanup(self):
        """Cleanup resources before exit"""
        print("\n🧹 Cleaning up resources...")
        self.logger.info("Cleaning up TriSense AI resources")
        
        # Stop all modules
        if self.vision_module:
            try:
                self.vision_module.stop()
            except:
                pass
        
        if self.hearing_module:
            try:
                self.hearing_module.stop()
            except:
                pass
        
        if self.voice_module:
            try:
                self.voice_module.stop()
            except:
                pass
        
        # Stop TTS
        try:
            self.tts_engine.stop()
        except:
            pass
        
        print("Cleanup completed.")
        self.tts_engine.speak("Thank you for using TriSense AI. Goodbye!")
    
    def run(self):
        """Main application loop"""
        self.running = True
        self.display_welcome()
        
        try:
            while self.running:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == "1":
                    self.handle_vision_module()
                elif choice == "2":
                    self.handle_hearing_module()
                elif choice == "3":
                    self.handle_voice_module()
                elif choice == "4":
                    self.handle_settings()
                elif choice == "5":
                    self.handle_test_system()
                elif choice == "6":
                    self.handle_help()
                elif choice == "0":
                    self.running = False
                    break
                else:
                    print("Invalid choice. Please select 0-6.")
                    self.tts_engine.speak("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            self.running = False
        
        except Exception as e:
            self.logger.error(f"Main loop error: {e}")
            print(f"System error: {e}")
        
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    try:
        controller = TriSenseController()
        controller.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
