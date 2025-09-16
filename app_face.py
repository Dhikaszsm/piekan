
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
app.secret_key = os.environ.get('SECRET_KEY', 'fisheries-production-key-railway')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fisheries_face.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_kapal_database(app)
init_budidaya_database(app)
init_tangkap_database(app)
init_pdspkp_database(app)

# User database (demo users)
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
    
    # Admin & Legacy
    'user_budidaya': {'password': 'passwordbud', 'role': 'budidaya', 'full_name': 'Ahmad Budidaya'},
    'user_tangkap': {'password': 'passwordtang', 'role': 'tangkap', 'full_name': 'Budi Tangkap'},
    'user_pds': {'password': 'passwordpds', 'role': 'pdspkp', 'full_name': 'Citra PDSPKP'},
    'admin': {'password': 'admin123', 'role': 'admin', 'full_name': 'System Administrator'},
    'dhika': {'password': 'dhika123', 'role': 'admin', 'full_name': 'Dhika Admin'}  # Backup admin
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
    
    # Redirect to role-specific dashboard
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
    # Get budidaya benih analytics
    budidaya_analytics = get_budidaya_analytics(session['username'])
    
    # Get recent permintaan untuk histori
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

@app.route('/dashboard/tangkap')
@require_role('tangkap')
def dashboard_tangkap():
    # Get both general and specific analytics
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
    # Get PDSPKP mutu analytics
    pdspkp_analytics = get_pdspkp_analytics()
    
    # Get recent permohonan untuk histori
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

@app.route('/dashboard/admin')
@require_role('admin')
def dashboard_admin():
    analytics = get_kapal_analytics()
    enrolled_users = face_system.get_enrolled_users()
    
    stats = {
        'total_users': len(DEMO_USERS),
        'enrolled_faces': len(enrolled_users),
        'total_kapal': analytics['total_kapal'],
        'analytics': analytics
    }
    
    return render_template('dashboard_admin.html', stats=stats, enrolled_users=enrolled_users)

# ==================== FACE RECOGNITION ROUTES ====================

@app.route('/face/enrollment')
@require_role('any')
def face_enrollment_page():
    """
    Halaman untuk enroll face
    """
    return render_template('face_enrollment.html')

@app.route('/face/login')
def face_login_page():
    """
    Halaman login dengan face recognition
    """
    return render_template('face_login.html')

@app.route('/api/face/enroll', methods=['POST'])
@require_role('any')
def api_enroll_face():
    """
    API untuk enroll face
    """
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
        
        # Enroll face
        result = face_system.enroll_face(username, image_data, user_info)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/api/face/recognize', methods=['POST'])
def api_recognize_face():
    """
    API untuk face recognition login
    """
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data provided'})
        
        # Recognize face
        result = face_system.recognize_face(image_data)
        
        if result['success']:
            username = result['user']['username']
            
            # Check jika user ada di sistem
            if username in DEMO_USERS:
                # Create session (login user)
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

@app.route('/api/face/users')
@require_role('admin')
def api_face_users():
    """
    API untuk get enrolled users (admin only)
    """
    enrolled_users = face_system.get_enrolled_users()
    return jsonify({
        'success': True,
        'users': enrolled_users,
        'count': len(enrolled_users)
    })

@app.route('/api/face/delete/<username>', methods=['DELETE'])
@require_role('admin')
def api_delete_face_user(username):
    """
    API untuk delete enrolled user (admin only)
    """
    result = face_system.delete_user(username)
    return jsonify(result)

# ==================== KAPAL ROUTES ====================
# [Include all the kapal routes from previous app_kapal.py]

@app.route('/kapal/register', methods=['GET', 'POST'])
@require_role('any')
def register_kapal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            role = session.get('role')
            prefix = 'BD' if role == 'budidaya' else 'KL' if role == 'tangkap' else 'SR'
            count = Kapal.query.filter(Kapal.nomor_registrasi.like(f'{prefix}-%')).count() + 1
            nomor_registrasi = f'{prefix}-{count:03d}-{datetime.now().year}'
            
            ikan_target = request.form.getlist('ikan_target')
            if not ikan_target:
                ikan_target = request.form.get('ikan_target_manual', '').split(',')
                ikan_target = [ikan.strip() for ikan in ikan_target if ikan.strip()]
            
            kapal = Kapal(
                nama_kapal=request.form['nama_kapal'],
                nomor_registrasi=nomor_registrasi,
                jenis_kapal=role,
                ukuran_gt=float(request.form['ukuran_gt']) if request.form['ukuran_gt'] else None,
                ukuran_panjang=float(request.form['ukuran_panjang']) if request.form['ukuran_panjang'] else None,
                ukuran_lebar=float(request.form['ukuran_lebar']) if request.form['ukuran_lebar'] else None,
                ukuran_tinggi=float(request.form['ukuran_tinggi']) if request.form['ukuran_tinggi'] else None,
                nama_pemilik=request.form['nama_pemilik'],
                nik_pemilik=request.form['nik_pemilik'],
                alamat_pemilik=request.form['alamat_pemilik'],
                telepon_pemilik=request.form['telepon_pemilik'],
                pelabuhan_pangkalan=request.form['pelabuhan_pangkalan'],
                daerah_operasi=request.form['daerah_operasi'],
                alat_tangkap=request.form['alat_tangkap'],
                merk_mesin=request.form['merk_mesin'],
                kekuatan_mesin=float(request.form['kekuatan_mesin']) if request.form['kekuatan_mesin'] else None,
                jumlah_mesin=int(request.form['jumlah_mesin']) if request.form['jumlah_mesin'] else 1,
                registered_by=session['username'],
                masa_berlaku=datetime.now() + timedelta(days=365)
            )
            
            kapal.set_ikan_target(ikan_target)
            db.session.add(kapal)
            db.session.commit()
            
            flash(f'Kapal {kapal.nama_kapal} berhasil didaftarkan dengan nomor registrasi {nomor_registrasi}!')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saat mendaftarkan kapal: {str(e)}')
            print(f"[ERROR] Register kapal: {e}")
    
    return render_template('register_kapal.html', role=session.get('role'))

@app.route('/kapal/list')
@require_role('any')
def list_kapal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    
    if role in ['pdspkp', 'admin']:
        kapal_list = Kapal.query.all()
    else:
        kapal_list = Kapal.query.filter_by(registered_by=session['username']).all()
    
    return render_template('list_kapal.html', kapal_list=kapal_list, role=role)

@app.route('/kapal/detail/<int:kapal_id>')
@require_role('any')
def detail_kapal(kapal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    kapal = Kapal.query.get_or_404(kapal_id)
    
    role = session.get('role')
    if role not in ['pdspkp', 'admin'] and kapal.registered_by != session['username']:
        flash('Anda tidak memiliki akses untuk melihat kapal ini!')
        return redirect(url_for('list_kapal'))
    
    logistik = LogistikKapal.query.filter_by(kapal_id=kapal_id).order_by(
        LogistikKapal.tanggal_operasi.desc()
    ).limit(10).all()
    
    return render_template('detail_kapal.html', kapal=kapal, logistik=logistik)

@app.route('/api/kapal/analytics')
@require_role('any')
def api_kapal_analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    analytics = get_kapal_analytics()
    return jsonify({'success': True, 'analytics': analytics})

# ==================== BUDIDAYA BENIH ROUTES ====================

@app.route('/budidaya/permintaan/add', methods=['GET', 'POST'])
@require_role('budidaya')
def add_permintaan_benih():
    """
    Route untuk menambah permintaan benih ikan DO
    """
    if request.method == 'POST':
        try:
            # Generate nomor permintaan
            count = PermintaanBenih.query.filter_by(created_by=session['username']).count() + 1
            nomor_permintaan = f'BN-{count:03d}-{datetime.now().year}'
            
            # Calculate total biaya
            jumlah = int(request.form['jumlah_diminta']) if request.form['jumlah_diminta'] else 0
            harga = float(request.form['harga_per_ekor']) if request.form['harga_per_ekor'] else 0
            total_biaya = jumlah * harga
            
            # Create permintaan
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

@app.route('/budidaya/monitoring/add/<int:kolam_id>', methods=['GET', 'POST'])
@require_role('budidaya')  
def add_monitoring(kolam_id):
    """
    Route untuk menambah data monitoring harian
    """
    kolam = KolamBudidaya.query.get_or_404(kolam_id)
    
    # Check ownership
    if kolam.kapal.registered_by != session['username']:
        flash('Anda tidak memiliki akses ke kolam ini!')
        return redirect(url_for('dashboard_budidaya'))
    
    if request.method == 'POST':
        try:
            monitoring = MonitoringBudidaya(
                kolam_id=kolam_id,
                tanggal_monitoring=datetime.strptime(request.form['tanggal_monitoring'], '%Y-%m-%d').date(),
                ph_air=float(request.form['ph_air']) if request.form['ph_air'] else None,
                suhu_air=float(request.form['suhu_air']) if request.form['suhu_air'] else None,
                oksigen_terlarut=float(request.form['oksigen_terlarut']) if request.form['oksigen_terlarut'] else None,
                turbiditas=float(request.form['turbiditas']) if request.form['turbiditas'] else None,
                jumlah_pakan=float(request.form['jumlah_pakan']) if request.form['jumlah_pakan'] else None,
                frekuensi_pakan=int(request.form['frekuensi_pakan']) if request.form['frekuensi_pakan'] else None,
                jenis_pakan=request.form['jenis_pakan'],
                mortalitas=int(request.form['mortalitas']) if request.form['mortalitas'] else 0,
                kondisi_ikan=request.form['kondisi_ikan'],
                estimasi_berat=float(request.form['estimasi_berat']) if request.form['estimasi_berat'] else None,
                catatan=request.form['catatan'],
                cuaca=request.form['cuaca'],
                recorded_by=session['username']
            )
            
            db.session.add(monitoring)
            db.session.commit()
            
            flash(f'Data monitoring kolam {kolam.nomor_kolam} berhasil disimpan!')
            return redirect(url_for('dashboard_budidaya'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error menyimpan monitoring: {str(e)}')
    
    return render_template('add_monitoring_budidaya.html', kolam=kolam)

@app.route('/api/budidaya/analytics')
@require_role('budidaya')
def api_budidaya_analytics():
    """
    API untuk budidaya analytics
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    analytics = get_budidaya_analytics(session['username'])
    return jsonify({'success': True, 'budidaya': analytics})

# ==================== TANGKAP SPECIFIC ROUTES ====================

@app.route('/tangkap/trip/add', methods=['GET', 'POST'])
@require_role('tangkap')
def add_trip():
    """
    Route untuk menambah trip penangkapan
    """
    if request.method == 'POST':
        try:
            # Get kapal tangkap user
            kapal = Kapal.query.filter_by(
                jenis_kapal='tangkap',
                registered_by=session['username']
            ).first()
            
            if not kapal:
                flash('Anda belum memiliki kapal tangkap terdaftar!')
                return redirect(url_for('register_kapal'))
            
            # Generate trip number
            count = TripPenangkapan.query.filter_by(kapal_id=kapal.id).count() + 1
            nomor_trip = f'TR-{count:03d}-{datetime.now().year}'
            
            # Create trip
            trip = TripPenangkapan(
                kapal_id=kapal.id,
                nomor_trip=nomor_trip,
                tanggal_berangkat=datetime.strptime(request.form['tanggal_berangkat'], '%Y-%m-%dT%H:%M'),
                tanggal_kembali=datetime.strptime(request.form['tanggal_kembali'], '%Y-%m-%dT%H:%M') if request.form['tanggal_kembali'] else None,
                area_penangkapan=request.form['area_penangkapan'],
                koordinat_lat=float(request.form['koordinat_lat']) if request.form['koordinat_lat'] else None,
                koordinat_lon=float(request.form['koordinat_lon']) if request.form['koordinat_lon'] else None,
                kedalaman_air=float(request.form['kedalaman_air']) if request.form['kedalaman_air'] else None,
                kondisi_cuaca=request.form['kondisi_cuaca'],
                tinggi_gelombang=float(request.form['tinggi_gelombang']) if request.form['tinggi_gelombang'] else None,
                kecepatan_angin=float(request.form['kecepatan_angin']) if request.form['kecepatan_angin'] else None,
                bbm_berangkat=float(request.form['bbm_berangkat']) if request.form['bbm_berangkat'] else None,
                jumlah_abk=int(request.form['jumlah_abk']) if request.form['jumlah_abk'] else 1,
                nama_nahkoda=request.form['nama_nahkoda'],
                biaya_operasional=float(request.form['biaya_operasional']) if request.form['biaya_operasional'] else None,
                created_by=session['username']
            )
            
            db.session.add(trip)
            db.session.commit()
            
            flash(f'Trip {trip.nomor_trip} berhasil ditambahkan!')
            return redirect(url_for('dashboard_tangkap'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error menambah trip: {str(e)}')
    
    return render_template('add_trip_tangkap.html')

@app.route('/tangkap/hasil/add/<int:trip_id>', methods=['GET', 'POST'])
@require_role('tangkap')
def add_hasil_tangkapan(trip_id):
    """
    Route untuk menambah hasil tangkapan
    """
    trip = TripPenangkapan.query.get_or_404(trip_id)
    
    # Check ownership
    if trip.kapal.registered_by != session['username']:
        flash('Anda tidak memiliki akses ke trip ini!')
        return redirect(url_for('dashboard_tangkap'))
    
    if request.method == 'POST':
        try:
            # Calculate total nilai
            harga = float(request.form['harga_per_kg']) if request.form['harga_per_kg'] else 0
            berat = float(request.form['berat_kg']) if request.form['berat_kg'] else 0
            total_nilai = harga * berat
            
            hasil = HasilTangkapan(
                trip_id=trip_id,
                jenis_ikan=request.form['jenis_ikan'],
                berat_kg=berat,
                jumlah_ekor=int(request.form['jumlah_ekor']) if request.form['jumlah_ekor'] else None,
                ukuran_rata_rata=float(request.form['ukuran_rata_rata']) if request.form['ukuran_rata_rata'] else None,
                grade_a=float(request.form['grade_a']) if request.form['grade_a'] else 0,
                grade_b=float(request.form['grade_b']) if request.form['grade_b'] else 0,
                grade_c=float(request.form['grade_c']) if request.form['grade_c'] else 0,
                harga_per_kg=harga,
                total_nilai=total_nilai,
                pembeli=request.form['pembeli'],
                tempat_penjualan=request.form['tempat_penjualan'],
                alat_tangkap_utama=request.form['alat_tangkap_utama'],
                lokasi_tangkap=request.form['lokasi_tangkap']
            )
            
            db.session.add(hasil)
            db.session.commit()
            
            flash(f'Hasil tangkapan {hasil.jenis_ikan} berhasil dicatat!')
            return redirect(url_for('dashboard_tangkap'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error menyimpan hasil: {str(e)}')
    
    return render_template('add_hasil_tangkapan.html', trip=trip)

@app.route('/api/tangkap/analytics')
@require_role('tangkap')
def api_tangkap_analytics():
    """
    API untuk tangkap analytics
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    analytics = get_tangkap_analytics(session['username'])
    return jsonify({'success': True, 'tangkap': analytics})

# ==================== PDSPKP MUTU ROUTES ====================

@app.route('/pdspkp/permohonan/add', methods=['GET', 'POST'])
@require_role('pdspkp')
def add_permohonan_sertifikasi():
    """
    Route untuk menambah permohonan sertifikasi produk baru
    """
    if request.method == 'POST':
        try:
            # Generate nomor permohonan
            jenis = request.form['jenis_sertifikat']
            count = PermohonanSertifikasiProduk.query.filter_by(jenis_sertifikat=jenis).count() + 1
            nomor_permohonan = f'{jenis}-{count:03d}-{datetime.now().year}'
            
            # Calculate total biaya
            biaya_sertifikasi = float(request.form['biaya_sertifikasi']) if request.form['biaya_sertifikasi'] else 0
            biaya_audit = float(request.form['biaya_audit']) if request.form['biaya_audit'] else 0
            total_biaya = biaya_sertifikasi + biaya_audit
            
            # Create permohonan
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
            
            # Set anggota kunjungan
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
    """
    Route untuk menambah laporan monitoring mutu
    """
    if request.method == 'POST':
        try:
            # Generate nomor laporan
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
                produk_kadaluwarsa=int(request.form['produk_kadaluwarsa']) if request.form['produk_kadaluwarsa'] else 0,
                produk_tanpa_label=int(request.form['produk_tanpa_label']) if request.form['produk_tanpa_label'] else 0,
                produk_ikan_segar=int(request.form['produk_ikan_segar']) if request.form['produk_ikan_segar'] else 0,
                produk_ikan_olahan=int(request.form['produk_ikan_olahan']) if request.form['produk_ikan_olahan'] else 0,
                produk_ikan_frozen=int(request.form['produk_ikan_frozen']) if request.form['produk_ikan_frozen'] else 0,
                produk_ikan_kaleng=int(request.form['produk_ikan_kaleng']) if request.form['produk_ikan_kaleng'] else 0,
                produk_udang=int(request.form['produk_udang']) if request.form['produk_udang'] else 0,
                produk_lainnya=int(request.form['produk_lainnya']) if request.form['produk_lainnya'] else 0,
                produk_lokal=int(request.form['produk_lokal']) if request.form['produk_lokal'] else 0,
                produk_import=int(request.form['produk_import']) if request.form['produk_import'] else 0,
                tingkat_kepatuhan=float(request.form['tingkat_kepatuhan']) if request.form['tingkat_kepatuhan'] else 0,
                skor_higienitas=float(request.form['skor_higienitas']) if request.form['skor_higienitas'] else 0,
                skor_pelabelan=float(request.form['skor_pelabelan']) if request.form['skor_pelabelan'] else 0,
                tindakan_diambil=request.form['tindakan_diambil'],
                sanksi_diberikan=request.form['sanksi_diberikan'],
                petugas_monitoring=session['full_name'],
                created_by=session['username']
            )
            
            # Set negara asal import
            negara_import = request.form.get('negara_asal_import', '').split(',')
            negara_import = [n.strip() for n in negara_import if n.strip()]
            monitoring.set_negara_asal_import(negara_import)
            
            db.session.add(monitoring)
            db.session.commit()
            
            flash(f'Laporan monitoring {monitoring.nomor_laporan} berhasil dibuat!')
            return redirect(url_for('dashboard_pdspkp'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error membuat laporan monitoring: {str(e)}')
    
    return render_template('add_monitoring_mutu.html')

@app.route('/api/pdspkp/analytics')
@require_role('pdspkp')
def api_pdspkp_analytics():
    """
    API untuk PDSPKP analytics
    """
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
        'message': 'Fisheries System with Face Recognition is running',
        'session_active': 'user_id' in session,
        'kapal_count': analytics['total_kapal'],
        'enrolled_faces': len(enrolled_users),
        'face_system_ready': True
    })

if __name__ == '__main__':
    print("[INFO] Fisheries System - Face Recognition & Kapal Registration")
    print("=" * 60)
    print("[OK] http://localhost:8080")
    print("=" * 60)
    print("Login accounts available:")
    print("")
    print("[BUDIDAYA USERS]:")
    print("  - natalie / natalie123")
    print("  - putri / putri123")
    print("  - manda / manda123")
    print("  - besty / besty123")
    print("  - ari / ari123")
    print("")
    print("[TANGKAP USERS]:")
    print("  - fauzi / fauzi123")
    print("  - salman / salman123")
    print("  - fadlan / fadlan123")
    print("  - khairinal / khairinal123")
    print("")
    print("[PDSPKP USERS]:")
    print("  - elis / elis123")
    print("  - rahayu / rahayu123")
    print("  - dhilla / dhilla123")
    print("  - endah / endah123")
    print("")
    print("[ADMIN]:")
    print("  - admin / admin123")
    print("  - dhika / dhika123 (backup)")
    print("=" * 60)
    print("Features:")
    print("[FEATURE] OpenCV Face Recognition")
    print("[FEATURE] Face Enrollment & Login")
    print("[FEATURE] Kapal Registration")
    print("[FEATURE] Dashboard Analytics")
    print("[FEATURE] Role-based Access")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 8080))
    try:
        app.run(host='127.0.0.1', port=port, debug=True)
    except OSError as e:
        print(f"[ERROR] Cannot bind to port {port}: {e}")
        print("Try another port or check if the port is already in use")
