"""
Voice Module for TriSense AI
Text-to-speech proxy for mute users with quick shortcuts
"""

import os
import sys
import time
import threading
from typing import List, Dict, Optional
from datetime import datetime

from utils.tts_engine import get_tts_engine
from utils.logger import LoggerMixin, log_exception
from config.settings import Config


class ChatMessage:
    """Represents a chat message in the conversation"""
    
    def __init__(self, text: str, message_type: str = "user", timestamp: Optional[datetime] = None):
        self.text = text
        self.type = message_type  # "user", "system", "quick"
        self.timestamp = timestamp or datetime.now()
    
    def format_display(self) -> str:
        """Format message for display"""
        time_str = self.timestamp.strftime("%H:%M:%S")
        
        if self.type == "user":
            return f"[{time_str}] 🗣️ You: {self.text}"
        elif self.type == "quick":
            return f"[{time_str}] ⚡ Quick: {self.text}"
        elif self.type == "system":
            return f"[{time_str}] ℹ️ System: {self.text}"
        else:
            return f"[{time_str}] {self.text}"


class QuickPhrases:
    """Quick phrase shortcuts for common expressions"""
    
    PHRASES = {
        '1': {
            'text': "Hello, how are you?",
            'description': "Greeting",
            'category': "social"
        },
        '2': {
            'text': "I need help.",
            'description': "Request help",
            'category': "emergency"
        },
        '3': {
            'text': "Thank you.",
            'description': "Gratitude",
            'category': "social"
        },
        '4': {
            'text': "Yes, I understand.",
            'description': "Confirmation",
            'category': "response"
        },
        '5': {
            'text': "No, I don't understand.",
            'description': "Negative",
            'category': "response"
        },
        '6': {
            'text': "Please wait a moment.",
            'description': "Request patience",
            'category': "social"
        },
        '7': {
            'text': "I am feeling good today.",
            'description': "Status update",
            'category': "personal"
        },
        '8': {
            'text': "Can you repeat that?",
            'description': "Request repetition",
            'category': "clarification"
        },
        '9': {
            'text': "Goodbye!",
            'description': "Farewell",
            'category': "social"
        },
        '0': {
            'text': "Emergency! Please help me!",
            'description': "Emergency alert",
            'category': "emergency"
        }
    }
    
    @classmethod
    def get_phrase(cls, key: str) -> Optional[str]:
        """Get phrase by key"""
        phrase_data = cls.PHRASES.get(key)
        return phrase_data['text'] if phrase_data else None
    
    @classmethod
    def get_all_phrases(cls) -> Dict[str, Dict]:
        """Get all phrases with descriptions"""
        return cls.PHRASES.copy()
    
    @classmethod
    def get_phrases_by_category(cls, category: str) -> Dict[str, Dict]:
        """Get phrases by category"""
        return {k: v for k, v in cls.PHRASES.items() if v['category'] == category}


class VoiceInterface:
    """Terminal interface for voice module"""
    
    def __init__(self):
        self.messages: List[ChatMessage] = []
        self.max_messages = 20
        self.input_buffer = ""
        self.cursor_position = 0
    
    def add_message(self, text: str, message_type: str = "user"):
        """Add a message to the chat"""
        message = ChatMessage(text, message_type)
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display the chat interface header"""
        print("=" * 80)
        print("🗣️  TRISENSE AI - VOICE MODULE".center(80))
        print("Text-to-Speech Communication for Mute Users".center(80))
        print("=" * 80)
    
    def display_quick_phrases(self):
        """Display quick phrase shortcuts"""
        print("\n⚡ QUICK PHRASES (Press number key):")
        print("─" * 50)
        
        phrases = QuickPhrases.get_all_phrases()
        for key, phrase_data in phrases.items():
            category_icon = {
                'social': '💬',
                'emergency': '🚨',
                'response': '✅',
                'personal': '👤',
                'clarification': '❓'
            }.get(phrase_data['category'], '📝')
            
            print(f"  {key}. {category_icon} {phrase_data['text']} ({phrase_data['description']})")
        
        print("─" * 50)
    
    def display_messages(self):
        """Display chat messages"""
        if not self.messages:
            print("\n💭 No messages yet. Start typing or use quick phrases!")
            return
        
        print("\n💬 CONVERSATION HISTORY:")
        print("─" * 80)
        
        for message in self.messages[-10:]:  # Show last 10 messages
            print(message.format_display())
        
        print("─" * 80)
    
    def display_input_prompt(self):
        """Display input prompt"""
        print(f"\n📝 Type your message (or press 1-9 for quick phrases, 'q' to quit, 'c' to clear):")
        print(">", end=" ", flush=True)
    
    def get_user_input(self) -> str:
        """Get user input with special key handling"""
        try:
            user_input = input().strip()
            return user_input
        except KeyboardInterrupt:
            return 'q'
        except EOFError:
            return 'q'
    
    def display_full_interface(self):
        """Display the complete interface"""
        self.clear_screen()
        self.display_header()
        self.display_quick_phrases()
        self.display_messages()
        self.display_input_prompt()


class VoiceModule(LoggerMixin):
    """Voice Module for text-to-speech communication"""
    
    def __init__(self):
        """Initialize Voice Module"""
        super().__init__()
        self.config = Config.get_config('voice')
        self.tts_engine = get_tts_engine()
        
        # Interface
        self.interface = VoiceInterface()
        
        # State
        self.running = False
        self.speaking = False
        
        # Statistics
        self.message_count = 0
        self.quick_phrase_count = 0
        self.start_time = None
        
        self.logger.info("Voice Module initialized")
    
    def speak_text(self, text: str, message_type: str = "user") -> bool:
        """
        Convert text to speech and display in chat
        
        Args:
            text: Text to speak
            message_type: Type of message ("user", "quick", "system")
            
        Returns:
            True if speech successful, False otherwise
        """
        if not text or not text.strip():
            return False
        
        try:
            # Add to interface
            self.interface.add_message(text, message_type)
            
            # Speak the text
            success = self.tts_engine.speak(text)
            
            if success:
                self.message_count += 1
                if message_type == "quick":
                    self.quick_phrase_count += 1
                self.logger.info(f"Spoke: {text}")
            else:
                self.logger.error(f"Failed to speak: {text}")
            
            return success
            
        except Exception as e:
            log_exception(self.logger, e, f"Error speaking text: {text}")
            return False
    
    def handle_quick_phrase(self, key: str) -> bool:
        """
        Handle quick phrase selection
        
        Args:
            key: Quick phrase key (1-9, 0)
            
        Returns:
            True if phrase handled successfully, False otherwise
        """
        phrase = QuickPhrases.get_phrase(key)
        if phrase:
            return self.speak_text(phrase, "quick")
        return False
    
    def handle_user_input(self, user_input: str) -> bool:
        """
        Handle user input from interface
        
        Args:
            user_input: User input string
            
        Returns:
            True if input handled, False if should exit
        """
        user_input = user_input.strip()
        
        if not user_input:
            return True
        
        # Handle special commands
        if user_input.lower() in ['q', 'quit', 'exit']:
            return False
        elif user_input.lower() in ['c', 'clear']:
            self.interface.messages.clear()
            self.interface.add_message("Conversation cleared", "system")
            return True
        elif user_input.lower() in ['h', 'help']:
            self.show_help()
            return True
        elif user_input.isdigit() and len(user_input) == 1:
            # Quick phrase
            if self.handle_quick_phrase(user_input):
                return True
            else:
                self.interface.add_message(f"Invalid quick phrase: {user_input}", "system")
                return True
        else:
            # Regular text input
            return self.speak_text(user_input, "user")
    
    def show_help(self):
        """Display help information"""
        help_text = """
🗣️ VOICE MODULE HELP:

📝 REGULAR INPUT:
  • Type any message and press Enter to speak it
  • Your message will be spoken aloud and shown in history

⚡ QUICK PHRASES:
  • Press 1-9 or 0 for instant common phrases
  • No need to type - just press the number key

🎮 CONTROLS:
  • 'q' or 'quit' - Exit the module
  • 'c' or 'clear' - Clear conversation history
  • 'h' or 'help' - Show this help message

💡 TIPS:
  • Quick phrases are perfect for emergency situations
  • Your conversation history is preserved during the session
  • The system will speak everything you type
        """
        
        self.interface.add_message("Help displayed - see above", "system")
        print(help_text)
        input("\nPress Enter to continue...")
    
    def run_interface(self):
        """Main interface loop"""
        self.logger.info("Starting voice interface loop")
        
        while self.running:
            try:
                # Display interface
                self.interface.display_full_interface()
                
                # Get user input
                user_input = self.interface.get_user_input()
                
                # Handle input
                if not self.handle_user_input(user_input):
                    break
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                log_exception(self.logger, e, "Error in interface loop")
                time.sleep(0.1)
        
        self.logger.info("Voice interface loop ended")
    
    def start(self) -> bool:
        """
        Start the Voice Module
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting Voice Module")
            
            # Test TTS engine
            if not self.tts_engine.speak("Voice module activated", blocking=True):
                self.logger.error("TTS engine test failed")
                return False
            
            # Start timing
            self.start_time = time.time()
            
            # Add welcome message
            self.interface.add_message("Voice Module started. Type your messages or use quick phrases!", "system")
            
            # Start interface
            self.running = True
            self.run_interface()
            
            self.logger.info("Voice Module started successfully")
            return True
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to start Voice Module")
            return False
    
    def stop(self):
        """Stop the Voice Module"""
        try:
            self.logger.info("Stopping Voice Module")
            
            # Stop running
            self.running = False
            
            # Say goodbye
            self.speak_text("Voice module deactivated. Goodbye!", "system")
            
            # Clear screen
            self.interface.clear_screen()
            
            # Log statistics
            if self.start_time:
                duration = time.time() - self.start_time
                self.logger.info(f"Voice Module stopped. Stats: "
                               f"Duration: {duration:.1f}s, "
                               f"Messages: {self.message_count}, "
                               f"Quick phrases: {self.quick_phrase_count}")
            
        except Exception as e:
            log_exception(self.logger, e, "Error stopping Voice Module")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current status of Voice Module
        
        Returns:
            Dictionary containing status information
        """
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'running': self.running,
            'speaking': self.tts_engine.is_busy() if self.tts_engine else False,
            'message_count': self.message_count,
            'quick_phrase_count': self.quick_phrase_count,
            'duration': duration,
            'conversation_length': len(self.interface.messages),
            'tts_available': self.tts_engine is not None
        }
    
    def add_custom_phrase(self, key: str, text: str, description: str = "", category: str = "custom"):
        """
        Add a custom quick phrase
        
        Args:
            key: Key for the phrase (1-9, 0)
            text: Phrase text
            description: Description of the phrase
            category: Category for the phrase
        """
        try:
            QuickPhrases.PHRASES[key] = {
                'text': text,
                'description': description,
                'category': category
            }
            self.logger.info(f"Added custom phrase {key}: {text}")
            return True
        except Exception as e:
            log_exception(self.logger, e, f"Failed to add custom phrase {key}")
            return False
    
    def get_conversation_history(self) -> List[str]:
        """Get formatted conversation history"""
        return [msg.format_display() for msg in self.interface.messages]
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.interface.messages.clear()
        self.interface.add_message("Conversation cleared", "system")
        self.logger.info("Conversation cleared")
