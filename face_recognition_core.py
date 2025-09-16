# Core Face Recognition System untuk Fisheries
import face_recognition
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os
from datetime import datetime

class FaceRecognitionSystem:
    """
    Core system untuk face recognition operations
    Fungsi: Handle semua operasi computer vision untuk face detection dan recognition
    """
    
    def __init__(self, confidence_threshold=0.6):
        """
        Initialize face recognition system
        
        Args:
            confidence_threshold (float): Minimum confidence untuk accept recognition
            
        Fungsi: Setup parameters untuk face recognition
        """
        self.confidence_threshold = confidence_threshold
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # face_cascade = pre-trained model untuk detect faces di image
        
    def detect_faces_in_image(self, image_data):
        """
        Detect faces dalam image
        
        Args:
            image_data: Image dalam format numpy array atau PIL Image
            
        Returns:
            list: List of face locations [(top, right, bottom, left), ...]
            
        Fungsi: Find all faces di dalam image dan return coordinates
        """
        try:
            # Convert image ke format yang benar
            if isinstance(image_data, str):
                # Base64 string
                image_data = self.base64_to_image(image_data)
            
            # Convert PIL Image ke numpy array jika perlu
            if hasattr(image_data, 'convert'):
                image_array = np.array(image_data.convert('RGB'))
            else:
                image_array = image_data
            
            # Detect faces menggunakan face_recognition library
            face_locations = face_recognition.face_locations(image_array, model='hog')
            # model='hog' = Histogram of Oriented Gradients (faster, good accuracy)
            # model='cnn' = Convolutional Neural Network (slower, better accuracy)
            
            print(f"🔍 Detected {len(face_locations)} faces in image")
            return face_locations
            
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return []
    
    def extract_face_encoding(self, image_data, face_location=None):
        """
        Extract face encoding dari image
        
        Args:
            image_data: Image data
            face_location: Specific face location, atau None untuk auto-detect
            
        Returns:
            numpy.array: Face encoding (128-dimensional vector)
            
        Fungsi: Convert face image menjadi 128-dimensional encoding vector
        Yang bisa dibandingkan dengan face encodings lain
        """
        try:
            # Convert image
            if isinstance(image_data, str):
                image_data = self.base64_to_image(image_data)
                
            if hasattr(image_data, 'convert'):
                image_array = np.array(image_data.convert('RGB'))
            else:
                image_array = image_data
            
            # Extract face encodings
            if face_location:
                # Use specific face location
                encodings = face_recognition.face_encodings(image_array, [face_location])
            else:
                # Auto-detect face dan extract encoding
                encodings = face_recognition.face_encodings(image_array)
            
            if len(encodings) > 0:
                # Return first face encoding
                encoding = encodings[0]
                print(f"✅ Face encoding extracted: {len(encoding)} dimensions")
                return encoding
            else:
                print("❌ No face encoding could be extracted")
                return None
                
        except Exception as e:
            print(f"❌ Face encoding error: {e}")
            return None
    
    def compare_faces(self, known_encoding, unknown_encoding, tolerance=None):
        """
        Compare two face encodings
        
        Args:
            known_encoding: Face encoding yang sudah dikenal
            unknown_encoding: Face encoding yang mau dibandingkan
            tolerance: Custom tolerance untuk comparison
            
        Returns:
            tuple: (is_match: bool, confidence: float)
            
        Fungsi: Bandingkan dua face encodings dan return apakah match + confidence score
        """
        try:
            if tolerance is None:
                tolerance = self.confidence_threshold
            
            # Calculate face distance
            face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            # face_distance: 0.0 = identical, 1.0 = completely different
            
            # Convert distance ke confidence
            confidence = 1 - face_distance  # Higher confidence = better match
            
            # Determine if it's a match
            is_match = face_distance <= tolerance
            
            print(f"🔍 Face comparison: distance={face_distance:.3f}, confidence={confidence:.3f}, match={is_match}")
            return is_match, confidence
            
        except Exception as e:
            print(f"❌ Face comparison error: {e}")
            return False, 0.0
    
    def base64_to_image(self, base64_string):
        """
        Convert base64 string ke PIL Image
        
        Args:
            base64_string: Base64 encoded image data
            
        Returns:
            PIL.Image: Image object
            
        Fungsi: Convert base64 data dari JavaScript camera ke Python Image object
        """
        try:
            # Remove data URL prefix jika ada
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert ke PIL Image
            image = Image.open(io.BytesIO(image_data))
            return image
            
        except Exception as e:
            print(f"❌ Base64 conversion error: {e}")
            return None
    
    def save_face_photo(self, image_data, user_id, photo_type='enrollment'):
        """
        Save face photo ke file system
        
        Args:
            image_data: Image data
            user_id: User ID
            photo_type: Type of photo ('enrollment', 'attendance', 'verification')
            
        Returns:
            str: Filename jika berhasil, None jika gagal
            
        Fungsi: Simpan photo ke disk untuk audit trail dan debugging
        """
        try:
            # Create photos directory jika belum ada
            photos_dir = 'static/face_photos'
            if not os.path.exists(photos_dir):
                os.makedirs(photos_dir)
            
            # Generate filename dengan timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_{user_id}_{photo_type}_{timestamp}.jpg"
            filepath = os.path.join(photos_dir, filename)
            
            # Save image
            if isinstance(image_data, str):
                image_data = self.base64_to_image(image_data)
            
            # Convert ke RGB jika perlu
            if image_data.mode != 'RGB':
                image_data = image_data.convert('RGB')
                
            image_data.save(filepath, 'JPEG', quality=85)
            print(f"📸 Face photo saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Save photo error: {e}")
            return None
    
    def validate_face_quality(self, image_data):
        """
        Validate kualitas face image untuk enrollment
        
        Args:
            image_data: Image data
            
        Returns:
            dict: {'valid': bool, 'message': str, 'suggestions': list}
            
        Fungsi: Check apakah face image cukup bagus untuk reliable recognition
        """
        try:
            if isinstance(image_data, str):
                image_data = self.base64_to_image(image_data)
            
            image_array = np.array(image_data.convert('RGB'))
            
            # Check 1: Detect faces
            face_locations = face_recognition.face_locations(image_array)
            
            if len(face_locations) == 0:
                return {
                    'valid': False,
                    'message': 'Tidak ada wajah terdeteksi',
                    'suggestions': ['Pastikan wajah terlihat jelas', 'Coba pencahayaan yang lebih baik']
                }
            
            if len(face_locations) > 1:
                return {
                    'valid': False,
                    'message': 'Terdeteksi lebih dari 1 wajah',
                    'suggestions': ['Pastikan hanya ada 1 wajah di frame', 'Minta orang lain keluar dari frame']
                }
            
            # Check 2: Face size (harus cukup besar)
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top
            image_width, image_height = image_data.size
            
            face_percentage = (face_width * face_height) / (image_width * image_height)
            
            if face_percentage < 0.1:  # Face kurang dari 10% dari total image
                return {
                    'valid': False,
                    'message': 'Wajah terlalu kecil',
                    'suggestions': ['Dekatkan wajah ke kamera', 'Pastikan wajah mengisi minimal 20% frame']
                }
            
            # Check 3: Image quality (brightness, blur)
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Check brightness
            brightness = np.mean(gray)
            if brightness < 50:
                return {
                    'valid': False,
                    'message': 'Image terlalu gelap',
                    'suggestions': ['Tambah pencahayaan', 'Gunakan lampu yang lebih terang']
                }
            
            if brightness > 200:
                return {
                    'valid': False,
                    'message': 'Image terlalu terang',
                    'suggestions': ['Kurangi pencahayaan', 'Hindari backlight']
                }
            
            # Check blur (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                return {
                    'valid': False,
                    'message': 'Image terlalu blur',
                    'suggestions': ['Hold kamera lebih steady', 'Pastikan fokus yang baik']
                }
            
            # All checks passed
            return {
                'valid': True,
                'message': 'Kualitas wajah bagus untuk enrollment',
                'suggestions': []
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error validating face: {str(e)}',
                'suggestions': ['Coba ambil foto ulang', 'Pastikan format image correct']
            }

# Global face recognition system instance
face_system = FaceRecognitionSystem()
