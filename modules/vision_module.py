"""
Vision Module for TriSense AI
Object detection for blind users using YOLO and webcam
"""

import cv2
import time
import threading
from typing import Dict, List, Optional, Tuple
from ultralytics import YOLO

from utils.tts_engine import get_tts_engine
from utils.logger import LoggerMixin, log_exception
from config.settings import Config


class VisionModule(LoggerMixin):
    """Vision Module for real-time object detection and voice announcements"""
    
    def __init__(self):
        """Initialize Vision Module"""
        super().__init__()
        self.config = Config.get_config('vision')
        self.tts_engine = get_tts_engine()
        
        # YOLO Model
        self.model: Optional[YOLO] = None
        self.model_loaded = False
        
        # Camera
        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_active = False
        
        # Detection state
        self.running = False
        self.detection_thread: Optional[threading.Thread] = None
        
        # Cool-down timer logic
        self.last_announced_objects: Dict[str, float] = {}  # object_name -> timestamp
        self.cooldown_period = self.config.get('detection_cooldown', 5.0)  # seconds
        
        # Performance tracking
        self.frame_count = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Statistics
        self.detection_count = 0
        self.announcement_count = 0
        
        self.logger.info("Vision Module initialized")
    
    def load_model(self) -> bool:
        """
        Load YOLO model
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            model_path = self.config.get('model_path')
            self.logger.info(f"Loading YOLO model from: {model_path}")
            
            self.model = YOLO(model_path)
            self.model_loaded = True
            
            self.logger.info("YOLO model loaded successfully")
            return True
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to load YOLO model")
            return False
    
    def initialize_camera(self) -> bool:
        """
        Initialize webcam camera
        
        Returns:
            True if camera initialized successfully, False otherwise
        """
        try:
            camera_index = self.config.get('camera_index', 0)
            self.logger.info(f"Initializing camera at index: {camera_index}")
            
            self.cap = cv2.VideoCapture(camera_index)
            
            # Check if camera opened successfully
            if not self.cap.isOpened():
                self.logger.error("Failed to open camera")
                return False
            
            # Set camera properties
            width, height = self.config.get('window_size', (640, 480))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Test camera
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                self.logger.error("Camera test failed - no frame captured")
                self.cap.release()
                return False
            
            self.camera_active = True
            self.logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to initialize camera")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
    
    def should_announce_object(self, object_name: str) -> bool:
        """
        Check if object should be announced based on cool-down timer
        
        Args:
            object_name: Name of detected object
            
        Returns:
            True if object should be announced, False otherwise
        """
        current_time = time.time()
        
        # Check if object was announced recently
        if object_name in self.last_announced_objects:
            time_since_last = current_time - self.last_announced_objects[object_name]
            if time_since_last < self.cooldown_period:
                return False
        
        return True
    
    def announce_object(self, object_name: str):
        """
        Announce detected object using TTS
        
        Args:
            object_name: Name of object to announce
        """
        try:
            # Create announcement message
            message = f"I see {object_name}"
            
            # Announce asynchronously
            self.tts_engine.speak(message)
            
            # Update last announced time
            self.last_announced_objects[object_name] = time.time()
            self.announcement_count += 1
            
            self.logger.info(f"Announced: {message}")
            
        except Exception as e:
            log_exception(self.logger, e, f"Failed to announce object: {object_name}")
    
    def process_frame(self, frame: cv2.Mat) -> Tuple[cv2.Mat, List[str]]:
        """
        Process a single frame for object detection
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Tuple of (processed_frame, detected_objects)
        """
        detected_objects = []
        
        if not self.model_loaded:
            return frame, detected_objects
        
        try:
            # Run YOLO detection
            conf_threshold = self.config.get('confidence_threshold', 0.5)
            results = self.model(frame, conf=conf_threshold, verbose=False)
            
            # Process detection results
            if len(results) > 0 and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    # Get object information
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Get object name
                    object_name = self.model.names[cls_id]
                    detected_objects.append(object_name)
                    
                    # Check if should announce (cool-down logic)
                    if self.should_announce_object(object_name):
                        self.announce_object(object_name)
                
                # Draw bounding boxes and labels on frame
                annotated_frame = results[0].plot()
                self.detection_count += 1
            else:
                # No objects detected
                annotated_frame = frame.copy()
                
                # Optional: Announce "nothing detected" after some time
                if len(self.last_announced_objects) > 0:
                    # Check if it's been a while since any announcement
                    last_announcement = max(self.last_announced_objects.values())
                    if time.time() - last_announcement > 15:  # 15 seconds of silence
                        if self.should_announce_object("nothing"):
                            self.tts_engine.speak("No objects detected")
                            self.last_announced_objects["nothing"] = time.time()
            
            return annotated_frame, detected_objects
            
        except Exception as e:
            log_exception(self.logger, e, "Error processing frame")
            return frame, detected_objects
    
    def update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        self.fps_counter += 1
        
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:  # Update FPS every second
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def add_info_overlay(self, frame: cv2.Mat, detected_objects: List[str]) -> cv2.Mat:
        """
        Add information overlay to frame
        
        Args:
            frame: Input frame
            detected_objects: List of detected objects
            
        Returns:
            Frame with information overlay
        """
        # Create a copy to avoid modifying original
        overlay_frame = frame.copy()
        
        # Add FPS counter
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(overlay_frame, fps_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add detection count
        detection_text = f"Detections: {self.detection_count}"
        cv2.putText(overlay_frame, detection_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add current objects
        if detected_objects:
            objects_text = f"Objects: {', '.join(set(detected_objects))}"
            cv2.putText(overlay_frame, objects_text, (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Add instructions
        instructions = "Press 'q' to quit, 'c' to clear cooldown"
        cv2.putText(overlay_frame, instructions, (10, overlay_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return overlay_frame
    
    def detection_loop(self):
        """Main detection loop running in separate thread"""
        self.logger.info("Starting detection loop")
        
        frame_skip = self.config.get('frame_skip', 2)
        frame_counter = 0
        
        while self.running and self.camera_active:
            try:
                # Read frame from camera
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                frame_counter += 1
                
                # Process every nth frame for performance
                if frame_counter % frame_skip == 0:
                    processed_frame, detected_objects = self.process_frame(frame)
                else:
                    processed_frame, detected_objects = frame, []
                
                # Update FPS
                self.update_fps()
                
                # Add information overlay
                display_frame = self.add_info_overlay(processed_frame, detected_objects)
                
                # Display frame
                if self.config.get('display_window', True):
                    cv2.imshow("TriSense AI - Vision Module", display_frame)
                    
                    # Check for key presses
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('c'):
                        # Clear cooldown timers
                        self.last_announced_objects.clear()
                        self.logger.info("Cooldown timers cleared")
                
            except Exception as e:
                log_exception(self.logger, e, "Error in detection loop")
                time.sleep(0.1)
        
        self.logger.info("Detection loop ended")
    
    def start(self) -> bool:
        """
        Start the Vision Module
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting Vision Module")
            
            # Load model
            if not self.load_model():
                self.logger.error("Failed to load model")
                return False
            
            # Initialize camera
            if not self.initialize_camera():
                self.logger.error("Failed to initialize camera")
                return False
            
            # Start detection thread
            self.running = True
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()
            
            self.logger.info("Vision Module started successfully")
            return True
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to start Vision Module")
            return False
    
    def stop(self):
        """Stop the Vision Module"""
        try:
            self.logger.info("Stopping Vision Module")
            
            # Stop running
            self.running = False
            
            # Wait for detection thread to finish
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=2.0)
            
            # Release camera
            if self.cap:
                self.cap.release()
                self.cap = None
                self.camera_active = False
            
            # Close windows
            cv2.destroyAllWindows()
            
            # Log statistics
            self.logger.info(f"Vision Module stopped. Stats: "
                           f"Detections: {self.detection_count}, "
                           f"Announcements: {self.announcement_count}")
            
        except Exception as e:
            log_exception(self.logger, e, "Error stopping Vision Module")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current status of Vision Module
        
        Returns:
            Dictionary containing status information
        """
        return {
            'running': self.running,
            'model_loaded': self.model_loaded,
            'camera_active': self.camera_active,
            'current_fps': self.current_fps,
            'detection_count': self.detection_count,
            'announcement_count': self.announcement_count,
            'cooldown_objects': len(self.last_announced_objects),
            'cooldown_period': self.cooldown_period
        }
    
    def set_cooldown_period(self, seconds: float):
        """
        Update cool-down period for object announcements
        
        Args:
            seconds: Cool-down period in seconds
        """
        self.cooldown_period = max(1.0, seconds)  # Minimum 1 second
        self.config['detection_cooldown'] = self.cooldown_period
        self.logger.info(f"Cool-down period updated to {self.cooldown_period} seconds")
    
    def clear_cooldown_timers(self):
        """Clear all cool-down timers"""
        self.last_announced_objects.clear()
        self.logger.info("All cool-down timers cleared")
