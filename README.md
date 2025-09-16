# 🐟 Fisheries Management System
Sistem Informasi Perikanan Terintegrasi - Multi-Role Dashboard untuk Budidaya, Tangkap & Sertifikasi

## ✨ Fitur Utama
- 🎯 **Multi-Role Authentication** - Dashboard berbeda untuk setiap role
- 🌱 **Dashboard Budidaya** - Monitoring kolam, kualitas air, dan produksi
- 🎣 **Dashboard Tangkap** - Fleet management, cuaca laut, hasil tangkapan  
- 📜 **Dashboard Sertifikasi** - Manajemen permohonan dan approval workflow
- 🔒 **Role-Based Access Control** - Setiap user hanya akses dashboard sesuai role
- 📱 **Responsive Design** - Works on desktop, tablet, dan mobile
- ☁️ **Cloud Ready** - Siap deploy ke Railway, Heroku, atau cloud platform

## 🚀 Quick Start

### Local Development
```bash
# Clone repository
git clone [repository-url]
cd fisheries-system

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Cloud Deployment (Railway)
Lihat panduan lengkap: **[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)**

## 👤 User Accounts

| Role | Username | Password | Dashboard Access |
|------|----------|----------|------------------|
| 🌱 **Budidaya** | `user_budidaya` | `passwordbud` | Kolam monitoring, produksi, kualitas air |
| 🎣 **Tangkap** | `user_tangkap` | `passwordtang` | Fleet tracking, cuaca, hasil tangkapan |
| 📜 **Sertifikasi** | `user_pds` | `passwordpds` | Permohonan, approval, statistik |

## 🎨 Dashboard Features

### Dashboard Budidaya
- 📊 **Statistics**: Total kolam, produksi bulanan, kualitas air
- 🐟 **Data Kolam**: Status ikan, stok, umur, kondisi kesehatan
- ⚡ **Quick Actions**: Tambah kolam, cek air, laporan, manajemen pakan
- 🕐 **Activity Timeline**: Log aktivitas terbaru (pakan, monitoring, alert)

### Dashboard Tangkap  
- 📈 **Fleet Stats**: Kapal aktif, hasil tangkapan, nelayan, area tangkap
- 🚢 **Data Kapal**: Status kapal, kapten, area, hasil tangkapan
- 🌤️ **Weather Info**: Kondisi cuaca, angin, gelombang laut
- 🏆 **Top Species**: Statistik ikan terbanyak dengan persentase

### Dashboard Sertifikasi
- 📋 **Permohonan**: Total, disetujui, dalam proses, ditolak
- 📄 **Data Aplikasi**: Review permohonan, status approval, aksi
- ⚡ **Quick Actions**: Permohonan baru, generate sertifikat, laporan
- 📊 **Analytics**: Approval rate, processing time, statistik bulanan

## 🛠️ Tech Stack
- **Backend**: Python Flask 2.3.3
- **Frontend**: Bootstrap 5, Font Awesome 6, Custom CSS
- **Authentication**: Session-based dengan role protection
- **Deployment**: Railway (cloud) + Gunicorn WSGI server
- **Security**: CSRF protection, XSS headers, input validation

## 🌐 Deployment Options

### Option 1: Railway (Recommended)
```bash
# Follow RAILWAY_DEPLOY.md guide
# Result: https://[random].railway.app
```

### Option 2: Local Development
```bash
python app.py
# Access: http://localhost:5000
```

### Option 3: Local Network (LAN access)
```bash
python app.py  # app.py already configured for 0.0.0.0
# Access: http://[your-ip]:5000 from other devices
```

## 🔒 Security Features
- Session-based authentication
- Role-based access control (RBAC)
- Dashboard isolation per role
- XSS protection headers
- Input validation dan sanitization
- Secure session management

## 📱 Mobile Responsive
- ✅ Works on phones (iOS/Android)
- ✅ Works on tablets
- ✅ Responsive navigation
- ✅ Touch-friendly interface
- ✅ Optimized for small screens

## 🎯 Project Structure
```
fisheries-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Dependencies
├── Procfile              # Deployment config
├── railway.json          # Railway settings
├── runtime.txt           # Python version
├── templates/            # HTML templates
│   ├── base.html         # Base template dengan navbar
│   ├── login.html        # Login page
│   ├── welcome.html      # Welcome page after login
│   ├── dashboard_budidaya.html    # Budidaya dashboard
│   ├── dashboard_tangkap.html     # Tangkap dashboard
│   └── dashboard_pdspkp.html      # Sertifikasi dashboard
└── static/               # Static files (CSS/JS/Images)
```

## 🔄 Development Workflow

### Make Changes:
```bash
# Edit code
# Test locally: python app.py
# Commit changes: git add . && git commit -m "message"  
# Deploy: git push (Railway auto-deploys)
```

### Add New Features:
1. **Create new route** di `app.py`
2. **Create template** di `templates/`
3. **Add role protection** dengan `@require_role()` decorator
4. **Test locally** sebelum deploy
5. **Push to production**

## 📞 Support & Documentation

- 📖 **Deployment Guide**: [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)
- 🌐 **Live Demo**: [Coming after Railway deployment]
- 📧 **Issues**: Create GitHub issue untuk bug reports

## 🏆 Use Cases

- 🏢 **Perusahaan Perikanan**: Multi-departmental dashboard
- 🏛️ **Dinas Perikanan**: Role-based data management  
- 🎓 **Research**: Fish farming dan capture fisheries monitoring
- 📊 **Analytics**: Production dan certification tracking

---

**🐟 Fisheries Management System - Powering Indonesian Fisheries** 🇮🇩"
#tambahin auto face recog dan face enroll mengalami debugging server load #karena overload penyimpanan server dari cloud nya.if else nya kurang untuk #bida dengan menjadikan huer as a admin gabisa tapi in case kadang bisa masuk #dashboard an kadang gabisa masuk karena 1 orang 1 log lama kali ya? #bagaimana pun juga harus ada yang namanya face auth dan face db buat nyimpen #data base itunya okee
#penambahan fitur in bisa di github untuk for all userdiwaktu yang bersamaan agar railway ga bentrok juga dana apa bedanya dengan redis gwbelom nerapin sama sekali logika loginnya masih beleom jalan jadi bisa di input melalui input tambahan seperti face auth login yang di tarik ke database 