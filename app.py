# Fisheries System - Production Version for Railway
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from dotenv import load_dotenv
from kapal_models import db, Kapal, LogistikKapal, init_kapal_database, get_kapal_analytics
from budidaya_models import PermintaanBenih, StokBenih, DistribusiBenih, init_budidaya_database, get_budidaya_analytics
from tangkap_models import TripPenangkapan, HasilTangkapan, init_tangkap_database, get_tangkap_analytics
from pdspkp_models import PermohonanSertifikasiProduk, LaporanMonitoringMutu, init_pdspkp_database, get_pdspkp_analytics
from opencv_face_system import face_system
from datetime import datetime, date, timedelta
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'fisheries-production-key-railway-2024')

# Database configuration - PostgreSQL for production, SQLite for development
if os.environ.get('DATABASE_URL'):
    # Production on Railway
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fisheries_production.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize databases
init_kapal_database(app)
init_budidaya_database(app)
init_tangkap_database(app)
init_pdspkp_database(app)

# Production User Database
DEMO_USERS = {
    # Budidaya Users
    'natalie': {'password': 'natalie123', 'role': 'budidaya', 'full_name': 'Natalie Budidaya'},
    'putri': {'password': 'putri123', 'role': 'budidaya', 'full_name': 'Putri Budidaya'},
    'manda': {'password': 'manda123', 'role': 'budidaya', 'full_name': 'Manda Budidaya'},
    'besty': {'password': 'besty123', 'role': 'budidaya', 'full_name': 'Besty Budidaya'},
    'ari': {'password': 'ari123', 'role': 'budidaya', 'full_name': 'Ari Budidaya'},
    
    # Tangkap Users
    'fauzi': {'password': 'fauzi123', 'role': 'tangkap', 'full_name': 'Fauzi Tangkap'},
    'salman': {'password': 'salman123', 'role': 'tangkap', 'full_name': 'Salman Tangkap'},
    'fadlan': {'password': 'fadlan123', 'role': 'tangkap', 'full_name': 'Fadlan Tangkap'},
    'khairinal': {'password': 'khairinal123', 'role': 'tangkap', 'full_name': 'Khairinal Tangkap'},
    
    # PDSPKP Users  
    'elis': {'password': 'elis123', 'role': 'pdspkp', 'full_name': 'Elis PDSPKP'},
    'rahayu': {'password': 'rahayu123', 'role': 'pdspkp', 'full_name': 'Rahayu PDSPKP'},
    'dhilla': {'password': 'dhilla123', 'role': 'pdspkp', 'full_name': 'Dhilla PDSPKP'},
    'endah': {'password': 'endah123', 'role': 'pdspkp', 'full_name': 'Endah PDSPKP'},
    
    # Admin
    'admin': {'password': 'admin123', 'role': 'admin', 'full_name': 'System Administrator'},
    'dhika': {'password': 'dhika123', 'role': 'admin', 'full_name': 'Dhika Admin'}
}

# Decorator untuk proteksi role
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Silakan login terlebih dahulu!')
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role != required_role and required_role != 'any':
                flash(f'Akses ditolak! Anda tidak memiliki izin untuk mengakses dashboard {required_role.title()}.')
                return redirect(url_for('welcome'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Import semua routes dari app_face.py
# [Include all routes from app_face.py here for production]

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
        
        if username in DEMO_USERS and DEMO_USERS[username]['password'] == password:
            session['user_id'] = username
            session['username'] = username
            session['role'] = DEMO_USERS[username]['role']
            session['full_name'] = DEMO_USERS[username]['full_name']
            session['login_method'] = 'password'
            
            flash(f'Login berhasil! Selamat datang, {DEMO_USERS[username]["full_name"]} ({DEMO_USERS[username]["role"]}).')
            
            # Check if user needs face enrollment
            if username not in face_system.get_enrolled_users():
                flash('Untuk keamanan tambahan, silakan daftarkan wajah Anda untuk face login!')
                return redirect(url_for('face_enrollment_page'))
            
            return redirect(url_for('welcome'))
        else:
            flash('Username atau password salah!')
    
    return render_template('login_face.html')

@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('welcome_face.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    
    if role == 'budidaya':
        return redirect(url_for('dashboard_budidaya'))
    elif role == 'tangkap':
        return redirect(url_for('dashboard_tangkap'))
    elif role == 'pdspkp':
        return redirect(url_for('dashboard_pdspkp'))
    elif role == 'admin':
        return redirect(url_for('dashboard_admin'))
    else:
        flash('Role tidak dikenali!')
        return redirect(url_for('welcome'))

@app.route('/dashboard/budidaya')
@require_role('budidaya')
def dashboard_budidaya():
    try:
        budidaya_analytics = get_budidaya_analytics(session['username'])
        recent_permintaan = PermintaanBenih.query.filter_by(
            created_by=session['username']
        ).order_by(PermintaanBenih.created_at.desc()).limit(10).all()
        
        stats = {
            'total_permintaan': budidaya_analytics['total_permintaan'],
            'permintaan_disetujui': budidaya_analytics['permintaan_disetujui'],
            'permintaan_pending': budidaya_analytics['permintaan_pending'],
            'permintaan_ditolak': budidaya_analytics['permintaan_ditolak'],
            'budidaya': budidaya_analytics
        }
        
        return render_template('dashboard_budidaya_benih.html', stats=stats, recent_permintaan=recent_permintaan)
        
    except Exception as e:
        print(f"[ERROR] Budidaya dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}')
        return redirect(url_for('welcome'))

@app.route('/dashboard/tangkap')
@require_role('tangkap')
def dashboard_tangkap():
    analytics = get_kapal_analytics()
    tangkap_analytics = get_tangkap_analytics(session['username'])
    kapal_tangkap = Kapal.query.filter_by(jenis_kapal='tangkap', registered_by=session['username']).all()
    
    stats = {
        'total_kapal': len(kapal_tangkap),
        'kapal_aktif': len([k for k in kapal_tangkap if k.status_registrasi == 'aktif']),
        'total_gt': sum([k.ukuran_gt or 0 for k in kapal_tangkap]),
        'analytics': analytics,
        'tangkap': tangkap_analytics
    }
    
    return render_template('dashboard_tangkap_kapal.html', stats=stats, kapal_list=kapal_tangkap)

@app.route('/dashboard/pdspkp')
@require_role('pdspkp')
def dashboard_pdspkp():
    try:
        pdspkp_analytics = get_pdspkp_analytics()
        recent_permohonan = PermohonanSertifikasiProduk.query.order_by(
            PermohonanSertifikasiProduk.created_at.desc()
        ).limit(10).all()
        
        stats = {
            'total_permintaan': pdspkp_analytics['total_permintaan'],
            'sertifikasi_diterbitkan': pdspkp_analytics['sertifikasi_diterbitkan'],
            'dalam_proses': pdspkp_analytics['dalam_proses'],
            'ditolak': pdspkp_analytics['ditolak'],
            'pdspkp': pdspkp_analytics
        }
        
        return render_template('dashboard_pdspkp_mutu.html', stats=stats, recent_permohonan=recent_permohonan)
        
    except Exception as e:
        print(f"[ERROR] PDSPKP dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}')
        return redirect(url_for('welcome'))

@app.route('/dashboard/admin')
@require_role('admin')
def dashboard_admin():
    try:
        analytics = get_kapal_analytics()
        enrolled_users = face_system.get_enrolled_users()
        
        stats = {
            'total_users': len(DEMO_USERS),
            'enrolled_faces': len(enrolled_users),
            'total_kapal': analytics['total_kapal'],
            'analytics': analytics
        }
        
        return render_template('dashboard_admin.html', stats=stats, enrolled_users=enrolled_users)
        
    except Exception as e:
        print(f"[ERROR] Admin dashboard: {e}")
        flash(f'Error loading admin dashboard: {str(e)}')
        return redirect(url_for('welcome'))

# Admin Face Management Routes
@app.route('/api/face/users')
@require_role('admin')
def api_face_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    enrolled_users = face_system.get_enrolled_users()
    return jsonify({
        'success': True,
        'users': enrolled_users,
        'count': len(enrolled_users)
    })

@app.route('/api/face/delete/<username>', methods=['DELETE'])
@require_role('admin')
def api_delete_face_user(username):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    result = face_system.delete_user(username)
    return jsonify(result)

# Face Recognition Routes
@app.route('/face/enrollment')
@require_role('any')
def face_enrollment_page():
    return render_template('face_enrollment.html')

@app.route('/face/login')
def face_login_page():
    return render_template('face_login.html')

@app.route('/api/face/enroll', methods=['POST'])
@require_role('any')
def api_enroll_face():
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data provided'})
        
        username = session['username']
        user_info = {
            'role': session['role'],
            'full_name': session.get('full_name', username)
        }
        
        result = face_system.enroll_face(username, image_data, user_info)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/api/face/recognize', methods=['POST'])
def api_recognize_face():
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data provided'})
        
        result = face_system.recognize_face(image_data)
        
        if result['success']:
            username = result['user']['username']
            
            if username in DEMO_USERS:
                session['user_id'] = username
                session['username'] = username
                session['role'] = DEMO_USERS[username]['role']
                session['full_name'] = DEMO_USERS[username]['full_name']
                session['login_method'] = 'face_recognition'
                
                result['redirect_url'] = url_for('welcome')
                result['message'] = f"Welcome back, {DEMO_USERS[username]['full_name']}!"
            else:
                result['success'] = False
                result['message'] = 'User not found in system'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Recognition error: {str(e)}'})

# ==================== BUDIDAYA ROUTES ====================

@app.route('/budidaya/permintaan/add', methods=['GET', 'POST'])
@require_role('budidaya')
def add_permintaan_benih():
    if request.method == 'POST':
        try:
            count = PermintaanBenih.query.filter_by(created_by=session['username']).count() + 1
            nomor_permintaan = f'BN-{count:03d}-{datetime.now().year}'
            
            jumlah = int(request.form['jumlah_diminta']) if request.form['jumlah_diminta'] else 0
            harga = float(request.form['harga_per_ekor']) if request.form['harga_per_ekor'] else 0
            total_biaya = jumlah * harga
            
            permintaan = PermintaanBenih(
                nomor_permintaan=nomor_permintaan,
                tanggal_permintaan=datetime.strptime(request.form['tanggal_permintaan'], '%Y-%m-%d').date(),
                nama_pemohon=request.form['nama_pemohon'],
                alamat_pemohon=request.form['alamat_pemohon'],
                wilayah_dki=request.form['wilayah_dki'],
                telepon_pemohon=request.form['telepon_pemohon'],
                email_pemohon=request.form['email_pemohon'],
                jenis_usaha=request.form['jenis_usaha'],
                jenis_ikan=request.form['jenis_ikan'],
                ukuran_benih=request.form['ukuran_benih'],
                jumlah_diminta=jumlah,
                tujuan_budidaya=request.form['tujuan_budidaya'],
                alamat_kolam=request.form['alamat_kolam'],
                luas_kolam=float(request.form['luas_kolam']) if request.form['luas_kolam'] else None,
                jenis_kolam=request.form['jenis_kolam'],
                sumber_air=request.form['sumber_air'],
                harga_per_ekor=harga,
                total_biaya=total_biaya,
                catatan_pemohon=request.form['catatan_pemohon'],
                created_by=session['username']
            )
            
            db.session.add(permintaan)
            db.session.commit()
            
            flash(f'Permintaan benih {permintaan.nomor_permintaan} berhasil diajukan!')
            return redirect(url_for('dashboard_budidaya'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error mengajukan permintaan: {str(e)}')
    
    return render_template('add_permintaan_benih.html')

# ==================== PDSPKP ROUTES ====================

@app.route('/pdspkp/permohonan/add', methods=['GET', 'POST'])
@require_role('pdspkp')
def add_permohonan_sertifikasi():
    if request.method == 'POST':
        try:
            jenis = request.form['jenis_sertifikat']
            count = PermohonanSertifikasiProduk.query.filter_by(jenis_sertifikat=jenis).count() + 1
            nomor_permohonan = f'{jenis}-{count:03d}-{datetime.now().year}'
            
            biaya_sertifikasi = float(request.form['biaya_sertifikasi']) if request.form['biaya_sertifikasi'] else 0
            biaya_audit = float(request.form['biaya_audit']) if request.form['biaya_audit'] else 0
            total_biaya = biaya_sertifikasi + biaya_audit
            
            permohonan = PermohonanSertifikasiProduk(
                nomor_permohonan=nomor_permohonan,
                tanggal_permohonan=datetime.strptime(request.form['tanggal_permohonan'], '%Y-%m-%d').date(),
                nomor_surat=request.form['nomor_surat'],
                nama_pt=request.form['nama_pt'],
                alamat_pt=request.form['alamat_pt'],
                wilayah_dki=request.form['wilayah_dki'],
                contact_person=request.form['contact_person'],
                email=request.form['email'],
                telepon=request.form['telepon'],
                jenis_produk=request.form['jenis_produk'],
                nama_produk=request.form['nama_produk'],
                spesifikasi_produk=request.form['spesifikasi_produk'],
                jenis_sertifikat=jenis,
                tujuan_export=request.form['tujuan_export'],
                nomor_surat_tugas=request.form['nomor_surat_tugas'],
                tanggal_surat_tugas=datetime.strptime(request.form['tanggal_surat_tugas'], '%Y-%m-%d').date() if request.form['tanggal_surat_tugas'] else None,
                nomor_rekomtek=request.form['nomor_rekomtek'],
                tanggal_rekomtek=datetime.strptime(request.form['tanggal_rekomtek'], '%Y-%m-%d').date() if request.form['tanggal_rekomtek'] else None,
                tanggal_kunjungan=datetime.strptime(request.form['tanggal_kunjungan'], '%Y-%m-%d').date() if request.form['tanggal_kunjungan'] else None,
                periode_tahun_sertifikasi=int(request.form['periode_tahun_sertifikasi']) if request.form['periode_tahun_sertifikasi'] else datetime.now().year,
                biaya_sertifikasi=biaya_sertifikasi,
                biaya_audit=biaya_audit,
                total_biaya=total_biaya,
                created_by=session['username']
            )
            
            anggota_kunjungan = request.form.get('anggota_kunjungan', '').split(',')
            anggota_kunjungan = [a.strip() for a in anggota_kunjungan if a.strip()]
            permohonan.set_anggota_kunjungan(anggota_kunjungan)
            
            db.session.add(permohonan)
            db.session.commit()
            
            flash(f'Permohonan sertifikasi {permohonan.nomor_permohonan} berhasil dibuat!')
            return redirect(url_for('dashboard_pdspkp'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error membuat permohonan: {str(e)}')
    
    return render_template('add_permohonan_sertifikasi.html')

@app.route('/pdspkp/monitoring/add', methods=['GET', 'POST'])
@require_role('pdspkp')
def add_monitoring_mutu():
    if request.method == 'POST':
        try:
            count = LaporanMonitoringMutu.query.count() + 1
            nomor_laporan = f'MON-{count:03d}-{datetime.now().year}'
            
            monitoring = LaporanMonitoringMutu(
                nomor_laporan=nomor_laporan,
                tanggal_monitoring=datetime.strptime(request.form['tanggal_monitoring'], '%Y-%m-%d').date(),
                periode_bulan=int(request.form['periode_bulan']),
                periode_tahun=int(request.form['periode_tahun']),
                nama_lokasi=request.form['nama_lokasi'],
                alamat_lokasi=request.form['alamat_lokasi'],
                wilayah_dki=request.form['wilayah_dki'],
                jenis_lokasi=request.form['jenis_lokasi'],
                kategori_pengolah=request.form['kategori_pengolah'],
                jumlah_outlet=int(request.form['jumlah_outlet']) if request.form['jumlah_outlet'] else 0,
                jumlah_sampel=int(request.form['jumlah_sampel']) if request.form['jumlah_sampel'] else 0,
                produk_aman=int(request.form['produk_aman']) if request.form['produk_aman'] else 0,
                produk_tidak_aman=int(request.form['produk_tidak_aman']) if request.form['produk_tidak_aman'] else 0,
                tingkat_kepatuhan=float(request.form['tingkat_kepatuhan']) if request.form['tingkat_kepatuhan'] else 0,
                skor_higienitas=float(request.form['skor_higienitas']) if request.form['skor_higienitas'] else 0,
                skor_pelabelan=float(request.form['skor_pelabelan']) if request.form['skor_pelabelan'] else 0,
                petugas_monitoring=session['full_name'],
                created_by=session['username']
            )
            
            db.session.add(monitoring)
            db.session.commit()
            
            flash(f'Laporan monitoring {monitoring.nomor_laporan} berhasil dibuat!')
            return redirect(url_for('dashboard_pdspkp'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error membuat laporan monitoring: {str(e)}')
    
    return render_template('add_monitoring_mutu.html')

# API Routes
@app.route('/api/budidaya/analytics')
@require_role('budidaya')
def api_budidaya_analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    analytics = get_budidaya_analytics(session['username'])
    return jsonify({'success': True, 'budidaya': analytics})

@app.route('/api/pdspkp/analytics')
@require_role('pdspkp')
def api_pdspkp_analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    analytics = get_pdspkp_analytics()
    return jsonify({'success': True, 'pdspkp': analytics})

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.')
    return redirect(url_for('login'))

@app.route('/status')
def status():
    analytics = get_kapal_analytics()
    enrolled_users = face_system.get_enrolled_users()
    
    return jsonify({
        'status': 'OK',
        'message': 'Fisheries System Production - Face Recognition & Multi-Role Dashboard',
        'session_active': 'user_id' in session,
        'kapal_count': analytics['total_kapal'],
        'enrolled_faces': len(enrolled_users),
        'face_system_ready': True,
        'environment': 'production' if os.environ.get('DATABASE_URL') else 'development'
    })

if __name__ == '__main__':
    # Production mode setup
    print("=" * 60)
    print("🐟 FISHERIES SYSTEM - PRODUCTION READY")
    print("=" * 60)
    print("✅ Face Recognition with OpenCV")
    print("✅ Multi-Role Dashboard System")
    print("✅ Budidaya: Distribusi Benih DO")
    print("✅ Tangkap: Logbook Penangkapan") 
    print("✅ PDSPKP: Sertifikasi Mutu Produk")
    print("✅ DKI Jakarta Regional Support")
    print("=" * 60)
    print("🚀 Ready for Railway Deployment!")
    print("=" * 60)
    
    # Port configuration for Railway
    port = int(os.environ.get('PORT', 8080))
    debug_mode = not os.environ.get('DATABASE_URL')  # Debug off in production
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
