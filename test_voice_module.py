#!/usr/bin/env python3
"""
Test script for Voice Module
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.voice_module import VoiceModule

def test_voice_module():
    """Test the Voice Module"""
    print("🧪 Testing Voice Module...")
    
    try:
        # Initialize Voice Module
        voice_module = VoiceModule()
        print("✅ Voice Module initialized successfully")
        
        # Test TTS engine
        print("🔊 Testing TTS engine...")
        if voice_module.speak_text("Voice module test successful", "system"):
            print("✅ TTS engine working")
        else:
            print("❌ TTS engine failed")
            return False
        
        # Test quick phrases
        print("⚡ Testing quick phrases...")
        if voice_module.handle_quick_phrase('1'):
            print("✅ Quick phrase working")
        else:
            print("❌ Quick phrase failed")
        
        print("\n🎉 Voice Module test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_voice_module()
