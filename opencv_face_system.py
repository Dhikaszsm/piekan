# OpenCV Face Recognition System
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    print("[OK] OpenCV loaded successfully")
except ImportError as e:
    print(f"[WARNING] OpenCV not available: {e}")
    print("[INFO] Face recognition will be disabled")
    OPENCV_AVAILABLE = False
    # Mock numpy for fallback
    class MockNumpy:
        @staticmethod
        def frombuffer(*args, **kwargs):
            return None
        @staticmethod
        def max(*args, **kwargs):
            return 0.5
    np = MockNumpy()

import os
import base64
import json
from datetime import datetime

class OpenCVFaceSystem:
    """
    Face Recognition System menggunakan OpenCV
    Menggunakan LBPH (Local Binary Patterns Histograms) Face Recognizer
    """
    
    def __init__(self, faces_dir='faces_data'):
        """
        Initialize face recognition system
        """
        self.faces_dir = faces_dir
        self.model_file = os.path.join(faces_dir, 'face_model.yml')
        self.users_file = os.path.join(faces_dir, 'users.json')
        self.opencv_available = OPENCV_AVAILABLE
        
        # Create directory jika tidak ada
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
        
        if OPENCV_AVAILABLE:
            # Initialize face detector
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            # Use template matching for simple face recognition (demo purpose)
            self.use_simple_matching = True
        else:
            # Fallback mode - no face detection
            self.face_cascade = None
            self.use_simple_matching = False
            print("[INFO] Running in fallback mode without face detection")
        
        # Load model jika sudah ada
        self.users_data = self.load_users_data()
        self.load_model()
        
    def load_users_data(self):
        """Load user data dari file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_users_data(self):
        """Save user data ke file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users_data, f, indent=2)
    
    def load_model(self):
        """Load face templates (simplified version)"""
        if self.use_simple_matching:
            print("[OK] Simple face matching system ready")
            return True
        return False
    
    def base64_to_image(self, base64_string):
        """Convert base64 string to OpenCV image dengan preprocessing"""
        try:
            if not self.opencv_available:
                return None
                
            # Remove data URL prefix jika ada
            if 'data:image' in base64_string and 'base64,' in base64_string:
                base64_string = base64_string.split('base64,')[1]
            
            # Decode base64
            img_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print("[ERROR] Failed to decode image from base64")
                return None
            
            # Preprocessing untuk better detection
            # 1. Resize if too large
            height, width = image.shape[:2]
            if width > 1024 or height > 1024:
                scale = min(1024/width, 1024/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
                print(f"[DEBUG] Image resized to {new_width}x{new_height}")
            
            # 2. Improve contrast if needed
            gray_temp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray_temp)
            
            if avg_brightness < 80:  # Dark image
                # Increase brightness and contrast
                alpha = 1.3  # Contrast control
                beta = 30    # Brightness control
                image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
                print("[DEBUG] Applied brightness/contrast enhancement")
            
            print(f"[DEBUG] Image processed: {image.shape}, brightness: {avg_brightness:.1f}")
            return image
            
        except Exception as e:
            print(f"[ERROR] Base64 to image conversion: {e}")
            return None
    
    def detect_faces(self, image):
        """
        Detect faces dalam image dengan parameter yang lebih fleksibel
        Returns: list of face rectangles
        """
        try:
            if not self.opencv_available or image is None:
                return []
                
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Try multiple detection parameters untuk increased success rate
            detection_params = [
                # Parameter 1: Standard
                {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (80, 80)},
                # Parameter 2: More sensitive
                {'scaleFactor': 1.05, 'minNeighbors': 3, 'minSize': (60, 60)},
                # Parameter 3: Very sensitive
                {'scaleFactor': 1.03, 'minNeighbors': 2, 'minSize': (40, 40)},
                # Parameter 4: Ultra sensitive
                {'scaleFactor': 1.02, 'minNeighbors': 1, 'minSize': (30, 30)}
            ]
            
            for params in detection_params:
                faces = self.face_cascade.detectMultiScale(gray, **params)
                if len(faces) > 0:
                    print(f"[DEBUG] Face detected with params: {params}")
                    return faces
            
            print("[DEBUG] No faces detected with all parameter sets")
            return []
            
        except Exception as e:
            print(f"[ERROR] Face detection: {e}")
            return []
    
    def extract_face_roi(self, image, face_rect):
        """
        Extract face region of interest
        """
        try:
            x, y, w, h = face_rect
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2*padding)
            h = min(image.shape[0] - y, h + 2*padding)
            
            face_roi = image[y:y+h, x:x+w]
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Resize to consistent size
            gray_face = cv2.resize(gray_face, (200, 200))
            return gray_face
        except Exception as e:
            print(f"[ERROR] Face ROI extraction: {e}")
            return None
    
    def enroll_face(self, username, base64_image, user_info=None):
        """
        Enroll face untuk user tertentu
        """
        try:
            # Check if OpenCV available
            if not self.opencv_available:
                return {
                    'success': False,
                    'message': 'Face recognition not available on this server. Please use password login.'
                }
            
            # Convert base64 to image
            image = self.base64_to_image(base64_image)
            if image is None:
                return {
                    'success': False,
                    'message': 'Invalid image data'
                }
            
            # Detect faces
            faces = self.detect_faces(image)
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No face detected in image'
                }
            
            if len(faces) > 1:
                return {
                    'success': False,
                    'message': 'Multiple faces detected. Please ensure only one face is visible.'
                }
            
            # Extract face ROI
            face_roi = self.extract_face_roi(image, faces[0])
            if face_roi is None:
                return {
                    'success': False,
                    'message': 'Could not extract face region'
                }
            
            # Save face image
            user_id = len(self.users_data)
            face_filename = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            face_path = os.path.join(self.faces_dir, face_filename)
            cv2.imwrite(face_path, face_roi)
            
            # Add to users data
            self.users_data[username] = {
                'user_id': user_id,
                'face_file': face_filename,
                'enrolled_at': datetime.now().isoformat(),
                'user_info': user_info or {}
            }
            self.save_users_data()
            
            # Retrain model
            training_result = self.train_model()
            
            return {
                'success': True,
                'message': f'Face enrolled successfully for {username}',
                'face_file': face_filename,
                'training_success': training_result
            }
            
        except Exception as e:
            print(f"[ERROR] Face enrollment: {e}")
            return {
                'success': False,
                'message': f'Enrollment error: {str(e)}'
            }
    
    def train_model(self):
        """
        Simple face registration (no ML training needed for demo)
        """
        try:
            face_count = len(self.users_data)
            if face_count > 0:
                print(f"[OK] {face_count} face templates registered")
                return True
            else:
                print("[WARNING] No faces registered")
                return False
                
        except Exception as e:
            print(f"[ERROR] Face registration: {e}")
            return False
    
    def recognize_face(self, base64_image, confidence_threshold=80):
        """
        Simple face recognition using template matching (demo version)
        """
        try:
            # Check if OpenCV available
            if not self.opencv_available:
                return {
                    'success': False,
                    'message': 'Face recognition not available on this server. Please use password login.'
                }
            
            # Check if any faces enrolled
            if len(self.users_data) == 0:
                return {
                    'success': False,
                    'message': 'No faces enrolled. Please enroll faces first.'
                }
            
            # Convert base64 to image
            image = self.base64_to_image(base64_image)
            if image is None:
                return {
                    'success': False,
                    'message': 'Invalid image data'
                }
            
            # Detect faces
            faces = self.detect_faces(image)
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No face detected in image'
                }
            
            # Use first detected face
            face_roi = self.extract_face_roi(image, faces[0])
            if face_roi is None:
                return {
                    'success': False,
                    'message': 'Could not extract face region'
                }
            
            # Simple template matching with enrolled faces
            best_match = None
            best_score = 0
            
            for username, user_data in self.users_data.items():
                face_file = user_data['face_file']
                face_path = os.path.join(self.faces_dir, face_file)
                
                if os.path.exists(face_path):
                    template = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        # Simple correlation coefficient
                        correlation = cv2.matchTemplate(face_roi, template, cv2.TM_CCOEFF_NORMED)
                        max_score = float(np.max(correlation)) * 100  # Convert to Python float
                        
                        print(f"[DEBUG] {username}: {max_score:.1f}%")
                        
                        if max_score > best_score:
                            best_score = float(max_score)  # Ensure Python float
                            best_match = {
                                'username': username,
                                'user_info': user_data['user_info'],
                                'enrolled_at': user_data['enrolled_at']
                            }
            
            if best_match and best_score >= confidence_threshold:
                return {
                    'success': True,
                    'message': 'Face recognized successfully',
                    'user': best_match,
                    'confidence': best_score,
                    'match_percentage': best_score
                }
            else:
                return {
                    'success': False,
                    'message': 'Face not recognized or confidence too low',
                    'confidence': best_score,
                    'match_percentage': best_score
                }
            
        except Exception as e:
            print(f"[ERROR] Face recognition: {e}")
            return {
                'success': False,
                'message': f'Recognition error: {str(e)}'
            }
    
    def get_enrolled_users(self):
        """
        Get list of enrolled users
        """
        return list(self.users_data.keys())
    
    def delete_user(self, username):
        """
        Delete enrolled user dan face data
        """
        try:
            if username in self.users_data:
                # Delete face file
                face_file = self.users_data[username]['face_file']
                face_path = os.path.join(self.faces_dir, face_file)
                if os.path.exists(face_path):
                    os.remove(face_path)
                
                # Remove dari users data
                del self.users_data[username]
                self.save_users_data()
                
                # Retrain model
                if len(self.users_data) > 0:
                    self.train_model()
                
                return {
                    'success': True,
                    'message': f'User {username} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'User {username} not found'
                }
                
        except Exception as e:
            print(f"[ERROR] Delete user: {e}")
            return {
                'success': False,
                'message': f'Delete error: {str(e)}'
            }

# Global instance
face_system = OpenCVFaceSystem()
