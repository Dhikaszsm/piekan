from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from dotenv import load_dotenv
from redis_config import redis_manager, cache_result
from face_models import db, User, FaceData, Attendance, FaceRecognitionLog, init_face_database
from face_recognition_core import face_system
import json
from datetime import datetime, date

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fisheries-production-key-railway')

# Database configuration (SQLite untuk development, bisa diganti ke PostgreSQL untuk production)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fisheries_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_face_database(app)

# Decorator untuk proteksi role
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Silakan login terlebih dahulu!')
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role != required_role:
                flash(f'Akses ditolak! Anda tidak memiliki izin untuk mengakses dashboard {required_role.title()}.')
                return redirect(url_for('welcome'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple authentication untuk demo (tanpa database dulu)
        demo_users = {
            'user_budidaya': {'password': 'passwordbud', 'role': 'budidaya'},
            'user_tangkap': {'password': 'passwordtang', 'role': 'tangkap'},
            'user_pds': {'password': 'passwordpds', 'role': 'pdspkp'}
        }
        
        if username in demo_users and demo_users[username]['password'] == password:
            session['user_id'] = username
            session['username'] = username
            session['role'] = demo_users[username]['role']
            
            # Log login ke Redis
            redis_manager.increment_counter(f"login_count:{username}")
            redis_manager.increment_counter(f"login_count_role:{demo_users[username]['role']}")
            redis_manager.set_data(f"last_login:{username}", {
                'timestamp': str(__import__('datetime').datetime.now()),
                'role': demo_users[username]['role']
            }, expire_time=86400)  # Expire dalam 24 jam
            
            flash(f'Login berhasil! Selamat datang, {username} ({demo_users[username]["role"]}).')
            return redirect(url_for('welcome'))
        else:
            flash('Username atau password salah!')
    
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    
    # Redirect to role-specific dashboard
    if role == 'budidaya':
        return redirect(url_for('dashboard_budidaya'))
    elif role == 'tangkap':
        return redirect(url_for('dashboard_tangkap'))
    elif role == 'pdspkp':
        return redirect(url_for('dashboard_pdspkp'))
    else:
        flash('Role tidak dikenali!')
        return redirect(url_for('welcome'))

@app.route('/dashboard/budidaya')
@require_role('budidaya')
def dashboard_budidaya():
    # Get Redis statistics untuk dashboard
    login_count = redis_manager.get_data('login_count_role:budidaya') or 0
    last_login = redis_manager.get_data(f"last_login:{session['username']}")
    
    # Sample data untuk demo
    stats = {
        'total_kolam': 125,
        'produksi_bulan': 2.5,
        'kualitas_air': 'Good',
        'alerts': 3,
        'login_count': login_count,
        'last_login': last_login
    }
    
    return render_template('dashboard_budidaya.html', stats=stats)

@app.route('/dashboard/tangkap')
@require_role('tangkap')
def dashboard_tangkap():
    return render_template('dashboard_tangkap.html')

@app.route('/dashboard/pdspkp')
@require_role('pdspkp')
def dashboard_pdspkp():
    return render_template('dashboard_pdspkp.html')

@app.route('/logout')
def logout():
    # Log logout ke Redis
    if 'username' in session:
        redis_manager.set_data(f"last_logout:{session['username']}", {
            'timestamp': str(__import__('datetime').datetime.now()),
            'role': session.get('role')
        }, expire_time=86400)
    
    session.clear()
    flash('Anda telah logout.')
    return redirect(url_for('login'))

@app.route('/redis/status')
def redis_status():
    """
    API endpoint untuk monitoring Redis status
    Fungsi: Show Redis statistics dan health check
    """
    if 'user_id' not in session:
        return {'error': 'Not authenticated'}, 401
    
    try:
        # Get Redis info
        info = {
            'redis_connected': redis_manager.redis_client is not None,
            'total_keys': len(redis_manager.get_all_keys()),
            'login_stats': {
                'budidaya': redis_manager.get_data('login_count_role:budidaya') or 0,
                'tangkap': redis_manager.get_data('login_count_role:tangkap') or 0,
                'pdspkp': redis_manager.get_data('login_count_role:pdspkp') or 0
            },
            'current_user': {
                'username': session.get('username'),
                'role': session.get('role'),
                'login_count': redis_manager.get_data(f"login_count:{session['username']}") or 0
            }
        }
        return info
    except Exception as e:
        return {'error': str(e)}, 500

# ==================== FACE RECOGNITION ROUTES ====================

@app.route('/face/enrollment')
def face_enrollment_page():
    """
    Face enrollment page
    Fungsi: Halaman untuk register face user ke sistem
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('face_enrollment.html')

@app.route('/face/login')
def face_login_page():
    """
    Face recognition login page
    Fungsi: Halaman login menggunakan face recognition
    """
    return render_template('face_login.html')

@app.route('/api/enroll-face', methods=['POST'])
def api_enroll_face():
    """
    API endpoint untuk enroll face
    Fungsi: Process face enrollment dari camera capture
    """
    try:
        data = request.get_json()
        username = data.get('username')
        image_data = data.get('image_data')
        
        if not username or not image_data:
            return jsonify({'success': False, 'message': 'Missing username atau image data'})
        
        # Get user dari database
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': f'User {username} tidak ditemukan'})
        
        # Validate image quality
        quality_check = face_system.validate_face_quality(image_data)
        if not quality_check['valid']:
            return jsonify({
                'success': False,
                'message': quality_check['message'],
                'suggestions': quality_check['suggestions']
            })
        
        # Extract face encoding
        face_encoding = face_system.extract_face_encoding(image_data)
        if face_encoding is None:
            return jsonify({
                'success': False,
                'message': 'Tidak bisa extract face encoding',
                'suggestions': ['Pastikan wajah terlihat jelas', 'Coba pencahayaan yang lebih baik']
            })
        
        # Save photo (optional)
        photo_filename = face_system.save_face_photo(image_data, user.id, 'enrollment')
        
        # Check jika user sudah punya face data
        existing_face = FaceData.query.filter_by(user_id=user.id, is_primary=True).first()
        if existing_face:
            # Update existing face data
            existing_face.set_encoding_array(face_encoding)
            existing_face.photo_filename = photo_filename
            existing_face.created_at = datetime.utcnow()
        else:
            # Create new face data
            face_data = FaceData(
                user_id=user.id,
                photo_filename=photo_filename,
                is_primary=True
            )
            face_data.set_encoding_array(face_encoding)
            db.session.add(face_data)
        
        db.session.commit()
        
        # Log ke Redis
        redis_manager.set_data(f"face_enrolled:{username}", {
            'timestamp': str(datetime.now()),
            'photo_filename': photo_filename
        }, expire_time=86400)
        
        return jsonify({
            'success': True,
            'message': 'Face enrollment berhasil!',
            'user_info': user.to_dict(),
            'face_id': existing_face.id if existing_face else face_data.id,
            'confidence': 95,  # High confidence untuk enrollment
            'quality_score': 90
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/api/recognize-face', methods=['POST'])
def api_recognize_face():
    """
    API endpoint untuk face recognition login
    Fungsi: Process face recognition untuk login authentication
    """
    start_time = datetime.now()
    
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data provided'})
        
        # Extract face encoding dari image
        face_encoding = face_system.extract_face_encoding(image_data)
        if face_encoding is None:
            return jsonify({
                'success': False,
                'message': 'Tidak ada wajah Terdeteksi',
                'suggestions': ['Pastikan wajah di tengah frame', 'Coba pencahayaan lebih baik']
            })
        
        # Find matching user
        from face_models import get_user_by_face_encoding
        matched_user, confidence = get_user_by_face_encoding(face_encoding, confidence_threshold=0.6)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if matched_user and confidence:
            # Successful recognition
            
            # Create session (login user)
            session['user_id'] = matched_user.username
            session['username'] = matched_user.username
            session['role'] = matched_user.role
            session['login_method'] = 'face_recognition'
            
            # Log recognition success
            log_entry = FaceRecognitionLog(
                user_id=matched_user.id,
                recognized=True,
                confidence_score=confidence,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                processing_time_ms=int(processing_time)
            )
            db.session.add(log_entry)
            
            # Update face data last_used
            face_data = FaceData.query.filter_by(user_id=matched_user.id, is_primary=True).first()
            if face_data:
                face_data.last_used = datetime.utcnow()
            
            db.session.commit()
            
            # Log ke Redis
            redis_manager.increment_counter(f"face_login_count:{matched_user.username}")
            redis_manager.set_data(f"last_face_login:{matched_user.username}", {
                'timestamp': str(datetime.now()),
                'confidence': confidence,
                'processing_time_ms': processing_time
            }, expire_time=86400)
            
            return jsonify({
                'success': True,
                'message': 'Face recognition successful!',
                'user': matched_user.to_dict(),
                'confidence': round(confidence * 100, 2),
                'processing_time_ms': int(processing_time)
            })
        
        else:
            # Recognition failed
            log_entry = FaceRecognitionLog(
                recognized=False,
                confidence_score=confidence if confidence else 0,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                processing_time_ms=int(processing_time),
                error_message='No matching face found'
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': 'Wajah tidak dikenali dalam sistem',
                'suggestions': ['Pastikan Anda sudah melakukan face enrollment', 'Coba traditional login']
            })
        
    except Exception as e:
        # Log error
        log_entry = FaceRecognitionLog(
            recognized=False,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            error_message=str(e)
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'success': False, 'message': f'Recognition error: {str(e)}'})

@app.route('/attendance/clock-in', methods=['POST'])
def api_clock_in():
    """
    API untuk clock in attendance dengan face recognition
    Fungsi: Record attendance clock in menggunakan face scan
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        location = data.get('location', 'Office')
        
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check jika sudah clock in hari ini
        today = date.today()
        existing_attendance = Attendance.query.filter_by(
            user_id=user.id,
            date=today
        ).first()
        
        if existing_attendance and existing_attendance.clock_in:
            return jsonify({
                'success': False,
                'message': 'Anda sudah clock in hari ini',
                'clock_in_time': existing_attendance.clock_in.strftime('%H:%M:%S')
            })
        
        # Verify face jika image provided
        confidence_score = None
        if image_data:
            face_encoding = face_system.extract_face_encoding(image_data)
            if face_encoding:
                matched_user, confidence = get_user_by_face_encoding(face_encoding)
                if matched_user and matched_user.id == user.id:
                    confidence_score = confidence
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Face verification failed - wajah tidak cocok dengan akun login'
                    })
        
        # Create atau update attendance record
        if existing_attendance:
            existing_attendance.clock_in = datetime.utcnow()
            existing_attendance.confidence_score = confidence_score
            existing_attendance.ip_address = request.remote_addr
            existing_attendance.location = location
        else:
            attendance = Attendance(
                user_id=user.id,
                clock_in=datetime.utcnow(),
                date=today,
                confidence_score=confidence_score,
                recognition_method='face' if image_data else 'manual',
                ip_address=request.remote_addr,
                location=location
            )
            db.session.add(attendance)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Clock in berhasil!',
            'clock_in_time': datetime.utcnow().strftime('%H:%M:%S'),
            'confidence': round(confidence_score * 100, 2) if confidence_score else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/redis/monitor')
def redis_monitor():
    """
    Redis monitoring dashboard
    Fungsi: Web interface untuk monitoring Redis data
    """
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    # Get all Redis keys dan data
    all_keys = redis_manager.get_all_keys()
    redis_data = {}
    
    for key in all_keys[:20]:  # Limit 20 keys untuk performance
        redis_data[key] = redis_manager.get_data(key)
    
    stats = {
        'connected': redis_manager.redis_client is not None,
        'total_keys': len(all_keys),
        'sample_data': redis_data,
        'login_counters': {
            'budidaya': redis_manager.get_data('login_count_role:budidaya') or 0,
            'tangkap': redis_manager.get_data('login_count_role:tangkap') or 0,
            'pdspkp': redis_manager.get_data('login_count_role:pdspkp') or 0
        }
    }
    
    return render_template('redis_monitor.html', stats=stats)

if __name__ == '__main__':
    # Development mode
    print("🐟 Fisheries System - Development Mode")
    print("=" * 50)
    print("[OK] http://localhost:5000")
    print("[OK] http://fisheries-system.test:5000")
    print("=" * 50)
    print("Login accounts:")
    print("🌱 user_budidaya / passwordbud")
    print("🎣 user_tangkap / passwordtang")
    print("📜 user_pds / passwordpds")
    print("=" * 50)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
