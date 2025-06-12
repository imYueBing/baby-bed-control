#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Camera Management Module - Responsible for video capture and stream processing
"""

import cv2
import logging
import threading
import time
import numpy as np
from datetime import datetime
import os
# BEGIN AI FACE DETECTION IMPORTS
import tflite_runtime.interpreter as tflite
# END AI FACE DETECTION IMPORTS

# Configure logging
logger = logging.getLogger(__name__)

class CameraManager:
    """Camera management class, responsible for video capture and processing"""
    
    def __init__(self, resolution=(640, 480), framerate=30, use_picamera=True, 
                 enable_ai_face_detection=False, # AI feature switch
                 cascade_path="/home/jeong/opencv_cascades/haarcascade_frontalface_default.xml", # TODO: Make this configurable
                 tflite_model_path="/home/jeong/frontal_face_classifier.tflite" # TODO: Make this configurable
                ):
        """
        Initialize camera manager
        
        Args:
            resolution (tuple): Resolution (width, height)
            framerate (int): Frame rate
            use_picamera (bool): Whether to use Raspberry Pi camera
            enable_ai_face_detection (bool): Whether to enable AI face detection
            cascade_path (str): Path to Haar cascade model
            tflite_model_path (str): Path to TFLite model
        """
        self.resolution = resolution
        self.framerate = framerate
        self.use_picamera = use_picamera
        self.camera = None
        self.is_running = False
        self.is_recording = False
        self.recording_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.frame_available = threading.Event()
        self.clients = []
        self.clients_lock = threading.Lock()
        self.debug_window_active = False
        self.debug_thread = None

        # AI Face Detection attributes
        self.enable_ai_face_detection = enable_ai_face_detection
        self.face_cascade = None
        self.tflite_interpreter = None
        self.tflite_input_details = None
        self.tflite_output_details = None

        if self.enable_ai_face_detection:
            self._initialize_ai_models(cascade_path, tflite_model_path)
        
        # Initialize camera
        self._init_camera()
    
    def _init_camera(self):
        """Initialize camera"""
        try:
            logger.debug(f"Attempting to initialize camera with resolution: {self.resolution} (type: {type(self.resolution)}) and framerate: {self.framerate}")
            # Try to use PiCamera library (if available and enabled)
            if self.use_picamera:
                try:
                    from picamera2 import Picamera2
                    self.camera = Picamera2()
                    config = self.camera.create_video_configuration(
                        main={"size": self.resolution, "format": "RGB888"},
                        controls={"FrameRate": self.framerate}
                    )
                    self.camera.configure(config)
                    self.camera.start()
                    logger.info("Raspberry Pi camera initialized")
                except (ImportError, ModuleNotFoundError):
                    logger.warning("Could not import picamera2 module, falling back to OpenCV")
                    self.use_picamera = False
            
            # If not using PiCamera or import failed, use OpenCV
            if not self.use_picamera:
                self.camera = cv2.VideoCapture(0)
                # Add checks before accessing resolution elements
                if isinstance(self.resolution, list) and len(self.resolution) >= 2:
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                else:
                    logger.error(f"Invalid camera resolution format: {self.resolution}. Expected a list of two integers.")
                    # Handle error, maybe default to a safe resolution or raise an exception
                    # For now, let's just log and potentially let it fail later if OpenCV can't handle it
                self.camera.set(cv2.CAP_PROP_FPS, self.framerate)
                
                if not self.camera.isOpened():
                    raise RuntimeError("Could not open camera")
                
                logger.info("OpenCV camera initialized")
            
            # Start capture thread
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}", exc_info=True) # exc_info=True will print traceback
            self.camera = None
            self.is_running = False # Ensure is_running is set to False on failure
    
    def _initialize_ai_models(self, cascade_path, tflite_model_path):
        """Initialize AI face recognition models"""
        logger.info("Initializing AI face detection models...")
        # 1. Haar cascade path setup and loading
        # TODO: These paths should be made configurable (e.g., via settings file or env vars)
        # For now, using the provided paths.
        if not os.path.exists(cascade_path):
            logger.error(f"Haar cascade file not found: {cascade_path}")
            self.enable_ai_face_detection = False # Disable AI if model is missing
            return
        try:
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.info(f"Haar cascade loaded from {cascade_path}")
        except Exception as e:
            logger.error(f"Error loading Haar cascade from {cascade_path}: {e}")
            self.enable_ai_face_detection = False
            return

        # 2. TFLite model loading
        if not os.path.exists(tflite_model_path):
            logger.error(f"TFLite model file not found: {tflite_model_path}")
            self.enable_ai_face_detection = False # Disable AI if model is missing
            return
        try:
            self.tflite_interpreter = tflite.Interpreter(model_path=tflite_model_path)
            self.tflite_interpreter.allocate_tensors()
            self.tflite_input_details = self.tflite_interpreter.get_input_details()
            self.tflite_output_details = self.tflite_interpreter.get_output_details()
            logger.info(f"TFLite model loaded from {tflite_model_path}")
        except Exception as e:
            logger.error(f"Error loading TFLite model from {tflite_model_path}: {e}")
            self.enable_ai_face_detection = False
            return
        logger.info("AI face detection models initialized successfully.")

    def _apply_ai_face_detection(self, frame_to_process):
        """Apply AI face detection and classification on the given frame"""
        if not self.enable_ai_face_detection or self.face_cascade is None or self.tflite_interpreter is None:
            return frame_to_process

        gray = cv2.cvtColor(frame_to_process, cv2.COLOR_BGR2GRAY)
        # Parameters for detectMultiScale can be tuned
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

        for (x, y, w, h) in faces:
            face_roi = frame_to_process[y:y+h, x:x+w]
            
            try:
                # Preprocess for TFLite model
                face_resized = cv2.resize(face_roi, (self.tflite_input_details[0]['shape'][1], self.tflite_input_details[0]['shape'][2]))
            except cv2.error as e:
                # This can happen if the face ROI is empty or too small after detection adjustments
                logger.debug(f"Could not resize face ROI: {e}. Skipping this face.")
                continue 
            except Exception as e: # Catch any other unexpected errors during resize
                logger.warning(f"Unexpected error resizing face ROI: {e}. Skipping this face.")
                continue

            if face_resized.size == 0: # Double check if face_resized is empty
                logger.debug("Face ROI resized to an empty image. Skipping.")
                continue

            input_data = face_resized.astype(np.float32) / 255.0
            input_data = np.expand_dims(input_data, axis=0)

            self.tflite_interpreter.set_tensor(self.tflite_input_details[0]['index'], input_data)
            self.tflite_interpreter.invoke()
            output_data = self.tflite_interpreter.get_tensor(self.tflite_output_details[0]['index'])
            
            # Assuming output_data[0][0] is the probability for "Front"
            probability_front = output_data[0][0] 
            
            label = "Front" if probability_front >= 0.5 else "Non-Front"
            color = (0, 255, 0) if label == "Front" else (0, 0, 255)
            prob_text = f"{label} ({probability_front:.2f})"

            cv2.rectangle(frame_to_process, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame_to_process, prob_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        return frame_to_process
    
    def _capture_loop(self):
        """Loop for capturing video frames"""
        while self.is_running and self.camera:
            try:
                # Get frame
                if self.use_picamera:
                    # Use PiCamera API
                    frame = self.camera.capture_array()
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    success = True
                else:
                    # Use OpenCV
                    success, frame = self.camera.read()
                
                if success and frame is not None: # Added frame is not None check
                    # Apply AI face recognition (if enabled)
                    if self.enable_ai_face_detection:
                        frame = self._apply_ai_face_detection(frame)

                    # Add timestamp to frame
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(
                        frame, 
                        timestamp, 
                        (10, frame.shape[0] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (255, 255, 255), 
                        1, 
                        cv2.LINE_AA
                    )
                    
                    # Update current frame
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                    
                    # Set frame available event
                    self.frame_available.set()
                    
                    # Notify all clients
                    self._notify_clients()
                
                # Wait appropriate time to maintain frame rate
                time.sleep(1.0 / self.framerate)
                
            except Exception as e:
                logger.error(f"Error capturing video frame: {e}")
                time.sleep(1)  # Pause after error
    
    def _notify_clients(self):
        """Notify all registered clients that a new frame is available"""
        with self.clients_lock:
            # Create a copy of the client list to avoid modifying the list during iteration
            clients_copy = self.clients.copy()
        
        for callback in clients_copy:
            try:
                callback(self.get_frame())
            except Exception as e:
                logger.error(f"Error notifying client: {e}")
                # If callback fails, remove the client
                with self.clients_lock:
                    if callback in self.clients:
                        self.clients.remove(callback)
    
    def close(self):
        """Close camera and clean up resources"""
        self.is_running = False
        self.stop_recording()
        self.stop_debug_window()
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        
        if self.camera:
            if self.use_picamera:
                self.camera.stop()
                self.camera.close()
            else:
                self.camera.release()
            
            self.camera = None
            logger.info("Camera closed")
    
    def get_frame(self):
        """
        Get current video frame
        
        Returns:
            numpy.ndarray: BGR formatted video frame
        """
        if not self.is_running or self.current_frame is None:
            # Return a black image
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                black_frame, 
                "Camera Unavailable", 
                (180, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (255, 255, 255), 
                2, 
                cv2.LINE_AA
            )
            return black_frame
        
        # Wait for frame to be available
        self.frame_available.wait(timeout=1.0)
        
        # Get a copy of the current frame
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            else:
                return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def get_jpeg_frame(self, quality=90):
        """
        Get JPEG encoded current frame
        
        Args:
            quality (int): JPEG quality, range 0-100
            
        Returns:
            bytes: JPEG encoded video frame
        """
        frame = self.get_frame()
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if ret:
            return jpeg.tobytes()
        return None
    
    def register_client(self, callback):
        """
        Register a video frame client
        
        Args:
            callback (callable): Callback function to call when a new frame is available
        """
        with self.clients_lock:
            if callback not in self.clients:
                self.clients.append(callback)
    
    def unregister_client(self, callback):
        """
        Unregister a video frame client
        
        Args:
            callback (callable): Previously registered callback function
        """
        with self.clients_lock:
            if callback in self.clients:
                self.clients.remove(callback)
    
    def start_recording(self, output_path="videos"):
        """
        Start recording video
        
        Args:
            output_path (str): Output directory path
        """
        if self.is_recording:
            logger.warning("Already recording video")
            return False
        
        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Create output filename
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_file = os.path.join(output_path, filename)
        
        # Start recording
        self.is_recording = True
        self.recording_thread = threading.Thread(
            target=self._recording_loop,
            args=(output_file,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        logger.info(f"Starting to record video to {output_file}")
        return True
    
    def stop_recording(self):
        """Stop recording video"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
            logger.info("Video recording stopped")
    
    def _recording_loop(self, output_file):
        """Video recording loop"""
        try:
            # Set video codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                output_file, 
                fourcc, 
                self.framerate,
                self.resolution
            )
            
            while self.is_recording and self.is_running:
                # Get current frame and write to video
                frame = self.get_frame()
                if frame is not None:
                    out.write(frame)
                
                # Short sleep to reduce CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error recording video: {e}")
        finally:
            if 'out' in locals():
                out.release()
                logger.info(f"Recorded video saved to {output_file}")
                
    def start_debug_window(self, window_name="Camera Debug"):
        """
        Open a window on Raspberry Pi to display live camera capture
        
        Args:
            window_name (str): Window title
        
        Returns:
            bool: Whether the debug window was successfully started
        """
        if self.debug_window_active:
            logger.warning("Debug window already running")
            return False
            
        self.debug_window_active = True
        self.debug_window_name = window_name
        
        # Create and start debug window thread
        self.debug_thread = threading.Thread(
            target=self._debug_window_loop,
            args=(window_name,)
        )
        self.debug_thread.daemon = True
        self.debug_thread.start()
        
        logger.info(f"Started camera debug window: {window_name}")
        return True
        
    def stop_debug_window(self):
        """Stop debug window"""
        if not self.debug_window_active:
            return
            
        self.debug_window_active = False
        if self.debug_thread and self.debug_thread.is_alive():
            self.debug_thread.join(timeout=2)
            cv2.destroyAllWindows()
            logger.info("Camera debug window closed")
            
    def _debug_window_loop(self, window_name):
        """Debug window display loop"""
        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            # If running on Raspberry Pi, can set full screen
            try:
                # Check if running on Raspberry Pi
                with open('/proc/device-tree/model', 'r') as f:
                    if 'Raspberry Pi' in f.read():
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            except:
                pass
                
            while self.debug_window_active and self.is_running:
                # Get current frame and display in window
                frame = self.get_frame()
                if frame is not None:
                    # Add debug information
                    debug_frame = frame.copy()
                    cv2.putText(
                        debug_frame,
                        f"Resolution: {self.resolution[0]}x{self.resolution[1]} | FPS: {self.framerate}",
                        (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA
                    )
                    
                    # Display camera type
                    camera_type = "PiCamera" if self.use_picamera else "OpenCV"
                    cv2.putText(
                        debug_frame,
                        f"Camera: {camera_type} | Model: Raspberry Pi Camera Module 3 Standard",
                        (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA
                    )
                    
                    # Display frame
                    cv2.imshow(window_name, debug_frame)
                    
                # Check keyboard input, press ESC key to exit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC key
                    self.debug_window_active = False
                    break
                    
                # Short sleep to reduce CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error displaying debug window: {e}")
        finally:
            cv2.destroyAllWindows()
            logger.info("Debug window closed") 