# Database models untuk Face Recognition System
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """
    User model untuk authentication
    Fungsi: Store user data dan link ke face data
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # budidaya, tangkap, pdspkp
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship ke face data
    face_data = db.relationship('FaceData', backref='user', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'face_enrolled': len(self.face_data) > 0
        }

class FaceData(db.Model):
    """
    Face encoding data untuk setiap user
    Fungsi: Store face encodings untuk recognition
    """
    __tablename__ = 'face_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    face_encoding = db.Column(db.Text, nullable=False)  # JSON encoded face features
    photo_filename = db.Column(db.String(255), nullable=True)  # Optional: simpan foto
    confidence_threshold = db.Column(db.Float, default=0.6)  # Threshold untuk recognition
    is_primary = db.Column(db.Boolean, default=False)  # Primary face untuk user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)  # Terakhir dipakai untuk recognition
    
    def __repr__(self):
        return f'<FaceData user_id={self.user_id}>'
    
    def get_encoding_array(self):
        """
        Convert JSON face encoding ke numpy array
        Fungsi: Face encoding disimpan sebagai JSON string, convert ke array untuk processing
        """
        try:
            return json.loads(self.face_encoding)
        except:
            return None
    
    def set_encoding_array(self, encoding_array):
        """
        Simpan numpy array sebagai JSON string
        Fungsi: Convert numpy array ke JSON untuk disimpan di database
        """
        try:
            # Convert numpy array ke list, lalu ke JSON
            self.face_encoding = json.dumps(encoding_array.tolist())
        except:
            self.face_encoding = None

class Attendance(db.Model):
    """
    Attendance records untuk track clock in/out
    Fungsi: Store semua attendance records dengan timestamp
    """
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Attendance data
    clock_in = db.Column(db.DateTime, nullable=True)
    clock_out = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    # Recognition data
    recognition_method = db.Column(db.String(20), default='face')  # 'face', 'manual', 'card'
    confidence_score = db.Column(db.Float, nullable=True)  # Face recognition confidence
    photo_filename = db.Column(db.String(255), nullable=True)  # Photo saat attendance
    
    # Location & device info
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(100), nullable=True)  # Office location
    
    # Status
    status = db.Column(db.String(20), default='present')  # present, late, absent
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance {self.user_id} on {self.date}>'
    
    def get_duration(self):
        """
        Calculate work duration
        Fungsi: Hitung lama kerja dari clock_in ke clock_out
        """
        if self.clock_in and self.clock_out:
            duration = self.clock_out - self.clock_in
            return duration.total_seconds() / 3600  # Return hours
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'clock_in': self.clock_in.isoformat() if self.clock_in else None,
            'clock_out': self.clock_out.isoformat() if self.clock_out else None,
            'duration_hours': self.get_duration(),
            'status': self.status,
            'confidence_score': self.confidence_score,
            'recognition_method': self.recognition_method
        }

class FaceRecognitionLog(db.Model):
    """
    Log semua face recognition attempts
    Fungsi: Track semua percobaan recognition untuk security dan debugging
    """
    __tablename__ = 'face_recognition_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null jika unknown face
    
    # Recognition result
    recognized = db.Column(db.Boolean, default=False)
    confidence_score = db.Column(db.Float, nullable=True)
    matched_face_id = db.Column(db.Integer, db.ForeignKey('face_data.id'), nullable=True)
    
    # Request info
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)  # Simpan photo untuk audit
    
    # Metadata
    processing_time_ms = db.Column(db.Integer, nullable=True)  # Berapa lama process recognition
    error_message = db.Column(db.Text, nullable=True)  # Error jika gagal
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FaceLog {self.id}: {"✅" if self.recognized else "❌"}>'

# Utility functions untuk database operations
def init_face_database(app):
    """
    Initialize database dengan sample data
    Fungsi: Setup database tables dan create sample users
    """
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create sample users jika belum ada
        sample_users = [
            {
                'username': 'user_budidaya',
                'full_name': 'Budi Santoso',
                'email': 'budi@fisheries.com',
                'role': 'budidaya'
            },
            {
                'username': 'user_tangkap', 
                'full_name': 'Sari Nelayan',
                'email': 'sari@fisheries.com',
                'role': 'tangkap'
            },
            {
                'username': 'user_pds',
                'full_name': 'Dhilla', 
                'email': 'ahmad@fisheries.com',
                'role': 'pdspkp'
            }
        ]
        
        for user_data in sample_users:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(**user_data)
                db.session.add(user)
        
        db.session.commit()
        print("[OK] Face recognition database initialized!")

def get_user_by_face_encoding(face_encoding, confidence_threshold=0.6):
    """
    Find user berdasarkan face encoding
    Fungsi: Compare face encoding dengan semua stored faces di database
    
    Args:
        face_encoding: numpy array dari detected face
        confidence_threshold: minimum confidence untuk match
        
    Returns:
        tuple: (User object, confidence_score) atau (None, None)
    """
    import face_recognition
    
    # Get semua face data dari database
    all_faces = FaceData.query.filter_by(is_primary=True).all()
    
    best_match = None
    best_confidence = 0
    
    for face_data in all_faces:
        stored_encoding = face_data.get_encoding_array()
        if stored_encoding is None:
            continue
            
        # Compare faces
        try:
            # Calculate face distance (lower = more similar)
            face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
            
            # Convert distance ke confidence (higher = more confident)
            confidence = 1 - face_distance
            
            # Check jika ini match terbaik
            if confidence > confidence_threshold and confidence > best_confidence:
                best_match = face_data.user
                best_confidence = confidence
                
        except Exception as e:
            print(f"Face comparison error: {e}")
            continue
    
    return best_match, best_confidence if best_match else None
