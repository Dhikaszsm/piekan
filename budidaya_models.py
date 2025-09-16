# Models dan Functions khusus untuk Budidaya - Distribusi Benih Ikan
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json
from kapal_models import db

class PermintaanBenih(db.Model):
    """
    Model untuk permintaan benih ikan DO (Dropped Out)
    """
    __tablename__ = 'permintaan_benih'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Data Permintaan
    nomor_permintaan = db.Column(db.String(50), unique=True, nullable=False)
    tanggal_permintaan = db.Column(db.Date, nullable=False)
    
    # Data Pemohon
    nama_pemohon = db.Column(db.String(100), nullable=False)
    alamat_pemohon = db.Column(db.Text, nullable=False)
    wilayah_dki = db.Column(db.String(50))  # Jakarta Timur, Barat, Selatan, Utara, Kepulauan Seribu
    telepon_pemohon = db.Column(db.String(20))
    email_pemohon = db.Column(db.String(100))
    jenis_usaha = db.Column(db.String(50))  # individu, kelompok, koperasi, perusahaan
    
    # Data Benih yang Diminta
    jenis_ikan = db.Column(db.String(50), nullable=False)  # nila, lele, mas, gurame, patin
    ukuran_benih = db.Column(db.String(20))  # 3-5cm, 5-8cm, 8-12cm
    jumlah_diminta = db.Column(db.Integer, nullable=False)  # ekor
    tujuan_budidaya = db.Column(db.String(50))  # konsumsi, pembesaran, indukan
    
    # Data Lokasi Budidaya
    alamat_kolam = db.Column(db.Text)
    luas_kolam = db.Column(db.Float)  # m2
    jenis_kolam = db.Column(db.String(50))  # terpal, tanah, beton, keramba
    sumber_air = db.Column(db.String(50))  # sumur, sungai, pam, mata air
    
    # Status Permintaan
    status_permintaan = db.Column(db.String(20), default='pending')  # pending, disetujui, ditolak, selesai
    tanggal_persetujuan = db.Column(db.Date)
    tanggal_distribusi = db.Column(db.Date)
    
    # Data Distribusi (jika disetujui)
    jumlah_disetujui = db.Column(db.Integer)
    harga_per_ekor = db.Column(db.Float)
    total_biaya = db.Column(db.Float)
    sumber_benih = db.Column(db.String(100))  # BBI/BBAT asal benih
    
    # Catatan
    catatan_pemohon = db.Column(db.Text)
    catatan_petugas = db.Column(db.Text)
    alasan_penolakan = db.Column(db.Text)
    
    # Metadata
    created_by = db.Column(db.String(50))  # user yang input
    approved_by = db.Column(db.String(50))  # petugas yang approve
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nomor_permintaan': self.nomor_permintaan,
            'tanggal_permintaan': self.tanggal_permintaan.isoformat() if self.tanggal_permintaan else None,
            'nama_pemohon': self.nama_pemohon,
            'alamat_pemohon': self.alamat_pemohon,
            'wilayah_dki': self.wilayah_dki,
            'telepon_pemohon': self.telepon_pemohon,
            'email_pemohon': self.email_pemohon,
            'jenis_usaha': self.jenis_usaha,
            'jenis_ikan': self.jenis_ikan,
            'ukuran_benih': self.ukuran_benih,
            'jumlah_diminta': self.jumlah_diminta,
            'tujuan_budidaya': self.tujuan_budidaya,
            'alamat_kolam': self.alamat_kolam,
            'luas_kolam': self.luas_kolam,
            'jenis_kolam': self.jenis_kolam,
            'sumber_air': self.sumber_air,
            'status_permintaan': self.status_permintaan,
            'tanggal_persetujuan': self.tanggal_persetujuan.isoformat() if self.tanggal_persetujuan else None,
            'tanggal_distribusi': self.tanggal_distribusi.isoformat() if self.tanggal_distribusi else None,
            'jumlah_disetujui': self.jumlah_disetujui,
            'harga_per_ekor': self.harga_per_ekor,
            'total_biaya': self.total_biaya,
            'sumber_benih': self.sumber_benih,
            'catatan_pemohon': self.catatan_pemohon,
            'catatan_petugas': self.catatan_petugas,
            'alasan_penolakan': self.alasan_penolakan,
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StokBenih(db.Model):
    """
    Model untuk stok benih ikan yang tersedia
    """
    __tablename__ = 'stok_benih'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Data Benih
    jenis_ikan = db.Column(db.String(50), nullable=False)
    ukuran = db.Column(db.String(20), nullable=False)
    stok_tersedia = db.Column(db.Integer, default=0)
    harga_per_ekor = db.Column(db.Float)
    
    # Sumber
    sumber_benih = db.Column(db.String(100))  # BBI/BBAT
    tanggal_masuk = db.Column(db.Date)
    kualitas_grade = db.Column(db.String(10))  # A, B, C
    
    # Status
    status_stok = db.Column(db.String(20), default='tersedia')  # tersedia, habis, reserved
    
    # Metadata
    updated_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'jenis_ikan': self.jenis_ikan,
            'ukuran': self.ukuran,
            'stok_tersedia': self.stok_tersedia,
            'harga_per_ekor': self.harga_per_ekor,
            'sumber_benih': self.sumber_benih,
            'tanggal_masuk': self.tanggal_masuk.isoformat() if self.tanggal_masuk else None,
            'kualitas_grade': self.kualitas_grade,
            'status_stok': self.status_stok,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DistribusiBenih(db.Model):
    """
    Model untuk tracking distribusi benih yang sudah diberikan
    """
    __tablename__ = 'distribusi_benih'
    
    id = db.Column(db.Integer, primary_key=True)
    permintaan_id = db.Column(db.Integer, db.ForeignKey('permintaan_benih.id'), nullable=False)
    
    # Data Distribusi
    nomor_distribusi = db.Column(db.String(50), unique=True)
    tanggal_distribusi = db.Column(db.Date, nullable=False)
    jumlah_distribusi = db.Column(db.Integer, nullable=False)
    
    # Penerima
    nama_penerima = db.Column(db.String(100))
    tanda_tangan = db.Column(db.Boolean, default=False)
    
    # Transport
    metode_transport = db.Column(db.String(50))  # pickup, kirim, ambil sendiri
    kendaraan = db.Column(db.String(50))
    biaya_transport = db.Column(db.Float)
    
    # Quality Check
    kondisi_benih = db.Column(db.String(20))  # baik, sedang, buruk
    mortalitas_transport = db.Column(db.Float)  # persen
    
    # Metadata
    distributed_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    permintaan = db.relationship('PermintaanBenih', backref=db.backref('distribusi', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'permintaan_id': self.permintaan_id,
            'nomor_distribusi': self.nomor_distribusi,
            'tanggal_distribusi': self.tanggal_distribusi.isoformat() if self.tanggal_distribusi else None,
            'jumlah_distribusi': self.jumlah_distribusi,
            'nama_penerima': self.nama_penerima,
            'tanda_tangan': self.tanda_tangan,
            'metode_transport': self.metode_transport,
            'kendaraan': self.kendaraan,
            'biaya_transport': self.biaya_transport,
            'kondisi_benih': self.kondisi_benih,
            'mortalitas_transport': self.mortalitas_transport,
            'distributed_by': self.distributed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_budidaya_database(app):
    """
    Initialize budidaya database untuk benih ikan
    """
    with app.app_context():
        try:
            # Create tables (don't drop in production)
            db.create_all()
            print("[OK] Budidaya benih database tables created!")
            
            # Create sample data only if empty
            if PermintaanBenih.query.count() == 0:
                create_sample_budidaya_benih_data()
        except Exception as e:
            print(f"[ERROR] Budidaya database init: {e}")
            # Continue anyway - tables might already exist

def create_sample_budidaya_benih_data():
    """
    Create sample data untuk budidaya benih
    """
    try:
        # Sample stok benih
        sample_stok = [
            {
                'jenis_ikan': 'Nila',
                'ukuran': '3-5cm',
                'stok_tersedia': 50000,
                'harga_per_ekor': 150,
                'sumber_benih': 'BBI Sukabumi',
                'tanggal_masuk': date(2024, 2, 1),
                'kualitas_grade': 'A',
                'updated_by': 'natalie'
            },
            {
                'jenis_ikan': 'Lele',
                'ukuran': '5-8cm',
                'stok_tersedia': 75000,
                'harga_per_ekor': 200,
                'sumber_benih': 'BBAT Jambi',
                'tanggal_masuk': date(2024, 2, 5),
                'kualitas_grade': 'A',
                'updated_by': 'putri'
            },
            {
                'jenis_ikan': 'Mas',
                'ukuran': '5-8cm',
                'stok_tersedia': 25000,
                'harga_per_ekor': 300,
                'sumber_benih': 'BBI Cianjur',
                'tanggal_masuk': date(2024, 2, 10),
                'kualitas_grade': 'A',
                'updated_by': 'manda'
            }
        ]
        
        for stok_data in sample_stok:
            stok = StokBenih(**stok_data)
            db.session.add(stok)
        
        # Sample permintaan benih
        sample_permintaan = [
            {
                'nomor_permintaan': 'BN-001-2024',
                'tanggal_permintaan': date(2024, 3, 1),
                'nama_pemohon': 'Pak Joko Santoso',
                'alamat_pemohon': 'Jl. Raya Desa Sukamaju No. 45, Bogor',
                'wilayah_dki': 'Jakarta Timur',
                'telepon_pemohon': '081234567890',
                'email_pemohon': 'joko@email.com',
                'jenis_usaha': 'individu',
                'jenis_ikan': 'Nila',
                'ukuran_benih': '3-5cm',
                'jumlah_diminta': 5000,
                'tujuan_budidaya': 'konsumsi',
                'alamat_kolam': 'Belakang rumah, Desa Sukamaju',
                'luas_kolam': 100.0,
                'jenis_kolam': 'terpal',
                'sumber_air': 'sumur',
                'status_permintaan': 'disetujui',
                'tanggal_persetujuan': date(2024, 3, 3),
                'tanggal_distribusi': date(2024, 3, 5),
                'jumlah_disetujui': 5000,
                'harga_per_ekor': 150,
                'total_biaya': 750000,
                'sumber_benih': 'BBI Sukabumi',
                'catatan_pemohon': 'Untuk budidaya konsumsi keluarga',
                'created_by': 'natalie',
                'approved_by': 'natalie'
            },
            {
                'nomor_permintaan': 'BN-002-2024',
                'tanggal_permintaan': date(2024, 3, 5),
                'nama_pemohon': 'Kelompok Tani Mina Jaya',
                'alamat_pemohon': 'Desa Sumber Rejeki, Bekasi',
                'wilayah_dki': 'Jakarta Barat',
                'telepon_pemohon': '081987654321',
                'jenis_usaha': 'kelompok',
                'jenis_ikan': 'Lele',
                'ukuran_benih': '5-8cm',
                'jumlah_diminta': 15000,
                'tujuan_budidaya': 'pembesaran',
                'alamat_kolam': 'Area persawahan, Desa Sumber Rejeki',
                'luas_kolam': 500.0,
                'jenis_kolam': 'tanah',
                'sumber_air': 'sungai',
                'status_permintaan': 'pending',
                'catatan_pemohon': 'Untuk program budidaya kelompok',
                'created_by': 'putri'
            },
            {
                'nomor_permintaan': 'BN-003-2024',
                'tanggal_permintaan': date(2024, 2, 20),
                'nama_pemohon': 'CV Mina Sejahtera',
                'alamat_pemohon': 'Jl. Industri No. 12, Tangerang',
                'wilayah_dki': 'Kepulauan Seribu Utara',
                'telepon_pemohon': '021-5556789',
                'email_pemohon': 'admin@minasejahtera.com',
                'jenis_usaha': 'perusahaan',
                'jenis_ikan': 'Gurame',
                'ukuran_benih': '8-12cm',
                'jumlah_diminta': 2000,
                'tujuan_budidaya': 'indukan',
                'alamat_kolam': 'Kompleks Industri Tangerang',
                'luas_kolam': 200.0,
                'jenis_kolam': 'beton',
                'sumber_air': 'pam',
                'status_permintaan': 'ditolak',
                'alasan_penolakan': 'Stok benih gurame sedang kosong',
                'created_by': 'manda',
                'approved_by': 'besty'
            }
        ]
        
        for permintaan_data in sample_permintaan:
            permintaan = PermintaanBenih(**permintaan_data)
            db.session.add(permintaan)
        
        db.session.commit()
        print("[OK] Sample budidaya benih data created!")
    
    except Exception as e:
        print(f"[ERROR] Creating sample budidaya benih data: {e}")
        db.session.rollback()

def get_budidaya_analytics(username=None):
    """
    Get analytics khusus untuk budidaya benih ikan
    """
    try:
        # Filter by user if provided
        if username:
            permintaan_query = PermintaanBenih.query.filter_by(created_by=username)
        else:
            permintaan_query = PermintaanBenih.query
        
        # 4 Data Penting Dashboard
        total_permintaan = permintaan_query.count()
        permintaan_disetujui = permintaan_query.filter_by(status_permintaan='disetujui').count()
        permintaan_pending = permintaan_query.filter_by(status_permintaan='pending').count()
        permintaan_ditolak = permintaan_query.filter_by(status_permintaan='ditolak').count()
        
        # Stok analytics
        total_stok = db.session.query(db.func.sum(StokBenih.stok_tersedia)).scalar() or 0
        jenis_ikan_tersedia = StokBenih.query.filter(StokBenih.stok_tersedia > 0).count()
        
        # Distribusi analytics
        total_benih_distribusi = db.session.query(db.func.sum(PermintaanBenih.jumlah_disetujui)).filter(
            PermintaanBenih.status_permintaan == 'disetujui'
        ).scalar() or 0
        
        total_nilai_distribusi = db.session.query(db.func.sum(PermintaanBenih.total_biaya)).filter(
            PermintaanBenih.status_permintaan == 'disetujui'
        ).scalar() or 0
        
        # Jenis ikan populer
        jenis_ikan_stats = db.session.query(
            PermintaanBenih.jenis_ikan,
            db.func.sum(PermintaanBenih.jumlah_diminta).label('total_diminta')
        ).group_by(PermintaanBenih.jenis_ikan).order_by(db.text('total_diminta DESC')).limit(5).all()
        
        # Jenis usaha stats
        jenis_usaha_stats = db.session.query(
            PermintaanBenih.jenis_usaha,
            db.func.count(PermintaanBenih.id).label('count')
        ).group_by(PermintaanBenih.jenis_usaha).order_by(db.text('count DESC')).all()
        
        # Performance metrics
        approval_rate = (permintaan_disetujui / total_permintaan * 100) if total_permintaan > 0 else 0
        avg_luas_kolam = db.session.query(db.func.avg(PermintaanBenih.luas_kolam)).scalar() or 0
        
        return {
            # 4 Data Penting Dashboard
            'total_permintaan': total_permintaan,
            'permintaan_disetujui': permintaan_disetujui,
            'permintaan_pending': permintaan_pending,
            'permintaan_ditolak': permintaan_ditolak,
            
            # Stok & Distribusi
            'total_stok': total_stok,
            'jenis_ikan_tersedia': jenis_ikan_tersedia,
            'total_benih_distribusi': total_benih_distribusi,
            'total_nilai_distribusi': round(total_nilai_distribusi / 1000000, 1) if total_nilai_distribusi else 0,  # dalam juta
            
            # Performance
            'approval_rate': round(approval_rate, 1),
            'avg_luas_kolam': round(avg_luas_kolam, 1),
            
            # Analytics
            'jenis_ikan_stats': [
                {'jenis': j[0], 'total_diminta': j[1]} 
                for j in jenis_ikan_stats
            ],
            'jenis_usaha_stats': [
                {'jenis': u[0] or 'Tidak diset', 'jumlah': u[1]} 
                for u in jenis_usaha_stats
            ],
            
            # Target
            'target_bulan_ini': {
                'permintaan_baru': 25,
                'distribusi_target': 150000,  # ekor
                'revenue_target': 22.5  # juta
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Budidaya benih analytics: {e}")
        return {
            'total_permintaan': 0,
            'permintaan_disetujui': 0,
            'permintaan_pending': 0,
            'permintaan_ditolak': 0,
            'total_stok': 0,
            'jenis_ikan_tersedia': 0,
            'total_benih_distribusi': 0,
            'total_nilai_distribusi': 0,
            'approval_rate': 0,
            'avg_luas_kolam': 0,
            'jenis_ikan_stats': [],
            'jenis_usaha_stats': [],
            'target_bulan_ini': {
                'permintaan_baru': 0,
                'distribusi_target': 0,
                'revenue_target': 0
            }
        }
