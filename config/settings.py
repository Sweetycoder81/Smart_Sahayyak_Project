"""
Global configuration settings for TriSense AI
Centralized configuration management for all modules
"""

import os
from typing import Dict, Any

class Config:
    """Global configuration class for TriSense AI"""
    
    # System Settings
    APP_NAME = "TriSense AI"
    VERSION = "1.0.0"
    DEBUG = False
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    MODELS_DIR = os.path.join(ASSETS_DIR, "models")
    AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    # Vision Module Settings
    VISION_CONFIG = {
        "model_path": os.path.join(MODELS_DIR, "yolov8n.pt"),
        "confidence_threshold": 0.5,
        "detection_cooldown": 2.0,  # seconds between same object announcements
        "camera_index": 0,
        "frame_skip": 2,  # Process every nth frame for performance
        "display_window": True,
        "window_size": (640, 480)
    }
    
    # Hearing Module Settings
    HEARING_CONFIG = {
        "microphone_index": None,  # Auto-detect
        "sample_rate": 16000,
        "chunk_size": 1024,
        "silence_threshold": 0.5,
        "phrase_time_limit": 5,  # seconds
        "adjust_for_ambient_noise": True,
        "energy_threshold": 300,
        "display_font_size": 24,
        "max_display_lines": 10
    }
    
    # Voice Module Settings
    VOICE_CONFIG = {
        "tts_rate": 150,  # words per minute
        "tts_volume": 0.9,  # 0.0 to 1.0
        "voice_gender": "female",  # "male" or "female"
        "input_buffer_size": 1000,
        "auto_speak": True,  # Speak on Enter key
        "clear_input_after_speak": True
    }
    
    # TTS Engine Settings
    TTS_CONFIG = {
        "engine": "pyttsx3",
        "rate": 150,
        "volume": 0.9,
        "voice_id": None  # Auto-select
    }
    
    # Logging Settings
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_logging": True,
        "console_logging": True
    }
    
    # Performance Settings
    PERFORMANCE_CONFIG = {
        "max_fps": 30,
        "enable_gpu": True,  # Use GPU if available
        "threading": True,
        "async_tts": True
    }
    
    # UI Settings
    UI_CONFIG = {
        "console_colors": True,
        "ascii_art": True,
        "clear_screen": True,
        "animation": True
    }
    
    @classmethod
    def get_config(cls, module: str) -> Dict[str, Any]:
        """
        Get configuration for a specific module
        
        Args:
            module: Module name ('vision', 'hearing', 'voice', 'tts', etc.)
            
        Returns:
            Configuration dictionary for the module
        """
        config_map = {
            'vision': cls.VISION_CONFIG,
            'hearing': cls.HEARING_CONFIG,
            'voice': cls.VOICE_CONFIG,
            'tts': cls.TTS_CONFIG,
            'logging': cls.LOGGING_CONFIG,
            'performance': cls.PERFORMANCE_CONFIG,
            'ui': cls.UI_CONFIG
        }
        
        return config_map.get(module.lower(), {})
    
    @classmethod
    def update_config(cls, module: str, key: str, value: Any) -> bool:
        """
        Update a configuration value
        
        Args:
            module: Module name
            key: Configuration key
            value: New value
            
        Returns:
            True if update successful, False otherwise
        """
        config = cls.get_config(module)
        if key in config:
            config[key] = value
            return True
        return False
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        directories = [
            cls.BASE_DIR,
            cls.ASSETS_DIR,
            cls.MODELS_DIR,
            cls.AUDIO_DIR,
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str) -> str:
        """
        Get full path to a model file
        
        Args:
            model_name: Name of the model file
            
        Returns:
            Full path to the model file
        """
        return os.path.join(cls.MODELS_DIR, model_name)
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        Validate configuration settings
        
        Returns:
            Dictionary with validation results
        """
        results = {}
        
        # Check if model file exists
        model_path = cls.VISION_CONFIG["model_path"]
        results["model_exists"] = os.path.exists(model_path)
        
        # Check if directories are writable
        results["assets_writable"] = os.access(cls.ASSETS_DIR, os.W_OK) if os.path.exists(cls.ASSETS_DIR) else False
        results["logs_writable"] = os.access(cls.LOGS_DIR, os.W_OK) if os.path.exists(cls.LOGS_DIR) else False
        
        # Validate numeric values
        results["valid_tts_rate"] = isinstance(cls.TTS_CONFIG["rate"], int) and 50 <= cls.TTS_CONFIG["rate"] <= 500
        results["valid_tts_volume"] = isinstance(cls.TTS_CONFIG["volume"], (int, float)) and 0.0 <= cls.TTS_CONFIG["volume"] <= 1.0
        
        return results

# Initialize directories on import
Config.ensure_directories()
