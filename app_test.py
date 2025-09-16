from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fisheries-production-key-railway')

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
    # Sample data untuk demo
    stats = {
        'total_kolam': 125,
        'produksi_bulan': 2.5,
        'kualitas_air': 'Good',
        'alerts': 3
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
    session.clear()
    flash('Anda telah logout.')
    return redirect(url_for('login'))

@app.route('/status')
def status():
    """Simple status check"""
    return jsonify({
        'status': 'OK',
        'message': 'Fisheries System is running',
        'session_active': 'user_id' in session
    })

if __name__ == '__main__':
    # Development mode
    print("[INFO] Fisheries System - Test Mode (without face recognition)")
    print("=" * 50)
    print("[OK] http://localhost:8080")
    print("=" * 50)
    print("Login accounts:")
    print("[USER] user_budidaya / passwordbud")
    print("[USER] user_tangkap / passwordtang")
    print("[USER] user_pds / passwordpds")
    print("=" * 50)
    
    port = int(os.environ.get('PORT', 8080))
    try:
        app.run(host='127.0.0.1', port=port, debug=True)
    except OSError as e:
        print(f"[ERROR] Cannot bind to port {port}: {e}")
        print("Try another port or check if the port is already in use")
