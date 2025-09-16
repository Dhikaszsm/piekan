from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from dotenv import load_dotenv
from kapal_models import db, Kapal, LogistikKapal, init_kapal_database, get_kapal_analytics
from datetime import datetime, date, timedelta
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fisheries-production-key-railway')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fisheries_kapal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_kapal_database(app)

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
        
        # Simple authentication untuk demo
        demo_users = {
            'user_budidaya': {'password': 'passwordbud', 'role': 'budidaya'},
            'user_tangkap': {'password': 'passwordtang', 'role': 'tangkap'},
            'user_pds': {'password': 'passwordpds', 'role': 'pdspkp'}
        }
        
        if username in demo_users and demo_users[username]['password'] == password:
            session['user_id'] = username
            session['username'] = username
            session['role'] = demo_users[username]['role']
            
            flash(f'Login berhasil! Selamat datang, {username} ({demo_users[username]["role"]}).')
            return redirect(url_for('welcome'))
        else:
            flash('Username atau password salah!')
    
    return render_template('login_simple.html')

@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('welcome_simple.html')

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
    # Get kapal analytics
    analytics = get_kapal_analytics()
    
    # Filter kapal budidaya saja
    kapal_budidaya = Kapal.query.filter_by(
        jenis_kapal='budidaya', 
        registered_by=session['username']
    ).all()
    
    stats = {
        'total_kolam': 125,
        'produksi_bulan': 2.5,
        'kualitas_air': 'Good',
        'alerts': 3,
        'total_kapal': len(kapal_budidaya),
        'kapal_aktif': len([k for k in kapal_budidaya if k.status_registrasi == 'aktif']),
        'analytics': analytics
    }
    
    return render_template('dashboard_budidaya_kapal.html', stats=stats, kapal_list=kapal_budidaya)

@app.route('/dashboard/tangkap')
@require_role('tangkap')
def dashboard_tangkap():
    # Get kapal analytics
    analytics = get_kapal_analytics()
    
    # Filter kapal tangkap saja
    kapal_tangkap = Kapal.query.filter_by(
        jenis_kapal='tangkap',
        registered_by=session['username']
    ).all()
    
    stats = {
        'total_kapal': len(kapal_tangkap),
        'kapal_aktif': len([k for k in kapal_tangkap if k.status_registrasi == 'aktif']),
        'total_gt': sum([k.ukuran_gt or 0 for k in kapal_tangkap]),
        'analytics': analytics
    }
    
    return render_template('dashboard_tangkap_kapal.html', stats=stats, kapal_list=kapal_tangkap)

@app.route('/dashboard/pdspkp')
@require_role('pdspkp')
def dashboard_pdspkp():
    # Get semua kapal analytics untuk sertifikasi
    analytics = get_kapal_analytics()
    
    # Get semua kapal untuk sertifikasi
    semua_kapal = Kapal.query.all()
    
    stats = {
        'total_kapal_sistem': len(semua_kapal),
        'kapal_tersertifikasi': len([k for k in semua_kapal if k.status_registrasi == 'aktif']),
        'pending_sertifikasi': 5,
        'analytics': analytics
    }
    
    return render_template('dashboard_pdspkp_kapal.html', stats=stats, kapal_list=semua_kapal)

# ==================== KAPAL REGISTRATION ROUTES ====================

@app.route('/kapal/register', methods=['GET', 'POST'])
def register_kapal():
    """
    Route untuk registrasi kapal baru
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Generate nomor registrasi otomatis
            role = session.get('role')
            prefix = 'BD' if role == 'budidaya' else 'KL' if role == 'tangkap' else 'SR'
            count = Kapal.query.filter(Kapal.nomor_registrasi.like(f'{prefix}-%')).count() + 1
            nomor_registrasi = f'{prefix}-{count:03d}-{datetime.now().year}'
            
            # Parse ikan target
            ikan_target = request.form.getlist('ikan_target')
            if not ikan_target:
                ikan_target = request.form.get('ikan_target_manual', '').split(',')
                ikan_target = [ikan.strip() for ikan in ikan_target if ikan.strip()]
            
            # Create kapal object
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
                masa_berlaku=datetime.now() + timedelta(days=365)  # 1 tahun
            )
            
            # Set ikan target
            kapal.set_ikan_target(ikan_target)
            
            # Save to database
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
def list_kapal():
    """
    Route untuk melihat daftar kapal
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    
    # Filter berdasarkan role
    if role == 'pdspkp':
        # PDSPKP bisa lihat semua kapal
        kapal_list = Kapal.query.all()
    else:
        # User lain hanya bisa lihat kapal sendiri
        kapal_list = Kapal.query.filter_by(registered_by=session['username']).all()
    
    return render_template('list_kapal.html', kapal_list=kapal_list, role=role)

@app.route('/kapal/detail/<int:kapal_id>')
def detail_kapal(kapal_id):
    """
    Route untuk melihat detail kapal
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    kapal = Kapal.query.get_or_404(kapal_id)
    
    # Check akses
    role = session.get('role')
    if role != 'pdspkp' and kapal.registered_by != session['username']:
        flash('Anda tidak memiliki akses untuk melihat kapal ini!')
        return redirect(url_for('list_kapal'))
    
    # Get logistik data
    logistik = LogistikKapal.query.filter_by(kapal_id=kapal_id).order_by(
        LogistikKapal.tanggal_operasi.desc()
    ).limit(10).all()
    
    return render_template('detail_kapal.html', kapal=kapal, logistik=logistik)

@app.route('/api/kapal/<int:kapal_id>', methods=['GET'])
def api_kapal_detail(kapal_id):
    """
    API endpoint untuk get detail kapal
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    kapal = Kapal.query.get_or_404(kapal_id)
    
    # Check akses
    role = session.get('role')
    if role != 'pdspkp' and kapal.registered_by != session['username']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'success': True,
        'kapal': kapal.to_dict()
    })

@app.route('/api/kapal/analytics')
def api_kapal_analytics():
    """
    API endpoint untuk analytics data
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    analytics = get_kapal_analytics()
    return jsonify({
        'success': True,
        'analytics': analytics
    })

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.')
    return redirect(url_for('login'))

@app.route('/status')
def status():
    """Simple status check"""
    analytics = get_kapal_analytics()
    return jsonify({
        'status': 'OK',
        'message': 'Fisheries System with Kapal Registration is running',
        'session_active': 'user_id' in session,
        'kapal_count': analytics['total_kapal']
    })

if __name__ == '__main__':
    # Development mode
    print("[INFO] Fisheries System - Kapal Registration Mode")
    print("=" * 50)
    print("[OK] http://localhost:8080")
    print("=" * 50)
    print("Login accounts:")
    print("[USER] user_budidaya / passwordbud")
    print("[USER] user_tangkap / passwordtang")
    print("[USER] user_pds / passwordpds")
    print("=" * 50)
    print("Features:")
    print("[FEATURE] Kapal Registration")
    print("[FEATURE] Dashboard Analytics")
    print("[FEATURE] Role-based Access")
    print("=" * 50)
    
    port = int(os.environ.get('PORT', 8080))
    try:
        app.run(host='127.0.0.1', port=port, debug=True)
    except OSError as e:
        print(f"[ERROR] Cannot bind to port {port}: {e}")
        print("Try another port or check if the port is already in use")
