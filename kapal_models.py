# Model Database untuk Registrasi Kapal
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Kapal(db.Model):
    """
    Model untuk data registrasi kapal
    """
    __tablename__ = 'kapal'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Data Identitas Kapal
    nama_kapal = db.Column(db.String(100), nullable=False)
    nomor_registrasi = db.Column(db.String(50), unique=True, nullable=False)
    jenis_kapal = db.Column(db.String(50), nullable=False)  # Tangkap/Budidaya/Angkut
    ukuran_gt = db.Column(db.Float)  # Gross Tonnage
    ukuran_panjang = db.Column(db.Float)  # Meter
    ukuran_lebar = db.Column(db.Float)   # Meter  
    ukuran_tinggi = db.Column(db.Float)  # Meter
    
    # Data Pemilik
    nama_pemilik = db.Column(db.String(100), nullable=False)
    nik_pemilik = db.Column(db.String(20), nullable=False)
    alamat_pemilik = db.Column(db.Text)
    telepon_pemilik = db.Column(db.String(20))
    
    # Data Operasional
    pelabuhan_pangkalan = db.Column(db.String(100))
    daerah_operasi = db.Column(db.String(100))
    jenis_ikan_target = db.Column(db.Text)  # JSON array
    alat_tangkap = db.Column(db.String(50))
    
    # Data Mesin
    merk_mesin = db.Column(db.String(50))
    kekuatan_mesin = db.Column(db.Float)  # HP
    jumlah_mesin = db.Column(db.Integer, default=1)
    
    # Data Registrasi
    tanggal_registrasi = db.Column(db.DateTime, default=datetime.utcnow)
    status_registrasi = db.Column(db.String(20), default='aktif')  # aktif/nonaktif/expired
    masa_berlaku = db.Column(db.DateTime)
    
    # Metadata
    registered_by = db.Column(db.String(50))  # Username yang mendaftarkan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_ikan_target(self, ikan_list):
        """Set target ikan sebagai JSON array"""
        self.jenis_ikan_target = json.dumps(ikan_list)
    
    def get_ikan_target(self):
        """Get target ikan sebagai list"""
        if self.jenis_ikan_target:
            try:
                return json.loads(self.jenis_ikan_target)
            except:
                return []
        return []
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'nama_kapal': self.nama_kapal,
            'nomor_registrasi': self.nomor_registrasi,
            'jenis_kapal': self.jenis_kapal,
            'ukuran_gt': self.ukuran_gt,
            'ukuran_panjang': self.ukuran_panjang,
            'ukuran_lebar': self.ukuran_lebar,
            'ukuran_tinggi': self.ukuran_tinggi,
            'nama_pemilik': self.nama_pemilik,
            'nik_pemilik': self.nik_pemilik,
            'alamat_pemilik': self.alamat_pemilik,
            'telepon_pemilik': self.telepon_pemilik,
            'pelabuhan_pangkalan': self.pelabuhan_pangkalan,
            'daerah_operasi': self.daerah_operasi,
            'jenis_ikan_target': self.get_ikan_target(),
            'alat_tangkap': self.alat_tangkap,
            'merk_mesin': self.merk_mesin,
            'kekuatan_mesin': self.kekuatan_mesin,
            'jumlah_mesin': self.jumlah_mesin,
            'tanggal_registrasi': self.tanggal_registrasi.isoformat() if self.tanggal_registrasi else None,
            'status_registrasi': self.status_registrasi,
            'masa_berlaku': self.masa_berlaku.isoformat() if self.masa_berlaku else None,
            'registered_by': self.registered_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Kapal {self.nama_kapal} ({self.nomor_registrasi})>'

class LogistikKapal(db.Model):
    """
    Model untuk data logistik dan operasional kapal
    """
    __tablename__ = 'logistik_kapal'
    
    id = db.Column(db.Integer, primary_key=True)
    kapal_id = db.Column(db.Integer, db.ForeignKey('kapal.id'), nullable=False)
    
    # Data Logistik
    tanggal_operasi = db.Column(db.Date, nullable=False)
    jenis_operasi = db.Column(db.String(50))  # berangkat/pulang/maintenance
    lokasi = db.Column(db.String(100))
    koordinat_lat = db.Column(db.Float)
    koordinat_lon = db.Column(db.Float)
    
    # Data Hasil Tangkapan (jika aplikasi)
    hasil_tangkapan = db.Column(db.Text)  # JSON data
    berat_total = db.Column(db.Float)     # Kg
    nilai_estimasi = db.Column(db.Float)  # Rupiah
    
    # Data Bahan Bakar
    konsumsi_bbm = db.Column(db.Float)    # Liter
    biaya_operasional = db.Column(db.Float)  # Rupiah
    
    # Metadata
    catatan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    kapal = db.relationship('Kapal', backref=db.backref('logistik', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'kapal_id': self.kapal_id,
            'tanggal_operasi': self.tanggal_operasi.isoformat() if self.tanggal_operasi else None,
            'jenis_operasi': self.jenis_operasi,
            'lokasi': self.lokasi,
            'koordinat_lat': self.koordinat_lat,
            'koordinat_lon': self.koordinat_lon,
            'hasil_tangkapan': json.loads(self.hasil_tangkapan) if self.hasil_tangkapan else None,
            'berat_total': self.berat_total,
            'nilai_estimasi': self.nilai_estimasi,
            'konsumsi_bbm': self.konsumsi_bbm,
            'biaya_operasional': self.biaya_operasional,
            'catatan': self.catatan,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_kapal_database(app):
    """
    Initialize database kapal dan create tables
    """
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("[OK] Kapal database initialized!")
        
        # Create sample data jika belum ada
        if Kapal.query.count() == 0:
            sample_kapal = [
                {
                    'nama_kapal': 'Sinar Bahari 01',
                    'nomor_registrasi': 'KL-001-2024',
                    'jenis_kapal': 'tangkap',
                    'ukuran_gt': 15.5,
                    'ukuran_panjang': 12.0,
                    'ukuran_lebar': 3.5,
                    'ukuran_tinggi': 2.8,
                    'nama_pemilik': 'Budi Santoso',
                    'nik_pemilik': '3201234567890123',
                    'alamat_pemilik': 'Jl. Pelabuhan No. 45, Jakarta',
                    'telepon_pemilik': '081234567890',
                    'pelabuhan_pangkalan': 'Pelabuhan Muara Angke',
                    'daerah_operasi': 'Laut Jawa Utara',
                    'alat_tangkap': 'Jaring Insang',
                    'merk_mesin': 'Yanmar',
                    'kekuatan_mesin': 40.0,
                    'jumlah_mesin': 1,
                    'registered_by': 'user_tangkap',
                    'status_registrasi': 'aktif'
                },
                {
                    'nama_kapal': 'Mina Jaya 02',
                    'nomor_registrasi': 'BD-002-2024',
                    'jenis_kapal': 'budidaya',
                    'ukuran_gt': 8.2,
                    'ukuran_panjang': 8.5,
                    'ukuran_lebar': 2.8,
                    'ukuran_tinggi': 2.0,
                    'nama_pemilik': 'Sari Dewi',
                    'nik_pemilik': '3201234567890124',
                    'alamat_pemilik': 'Jl. Tambak No. 12, Bekasi',
                    'telepon_pemilik': '081234567891',
                    'pelabuhan_pangkalan': 'Pelabuhan Cilincing',
                    'daerah_operasi': 'Tambak Bekasi',
                    'alat_tangkap': 'Keramba Apung',
                    'merk_mesin': 'Honda',
                    'kekuatan_mesin': 15.0,
                    'jumlah_mesin': 1,
                    'registered_by': 'user_budidaya',
                    'status_registrasi': 'aktif'
                }
            ]
            
            for kapal_data in sample_kapal:
                # Set ikan target untuk contoh
                if kapal_data['jenis_kapal'] == 'tangkap':
                    ikan_target = ['Ikan Tongkol', 'Ikan Kembung', 'Ikan Tenggiri']
                else:
                    ikan_target = ['Ikan Lele', 'Ikan Nila', 'Ikan Mas']
                
                kapal = Kapal(**kapal_data)
                kapal.set_ikan_target(ikan_target)
                db.session.add(kapal)
            
            db.session.commit()
            print("[OK] Sample kapal data created!")

def get_kapal_analytics():
    """
    Get analytics data untuk dashboard
    """
    try:
        total_kapal = Kapal.query.count()
        kapal_tangkap = Kapal.query.filter_by(jenis_kapal='tangkap').count()
        kapal_budidaya = Kapal.query.filter_by(jenis_kapal='budidaya').count()
        kapal_aktif = Kapal.query.filter_by(status_registrasi='aktif').count()
        
        # Kapal terbaru (5 terakhir)
        kapal_terbaru = Kapal.query.order_by(Kapal.created_at.desc()).limit(5).all()
        
        # Total GT
        total_gt = db.session.query(db.func.sum(Kapal.ukuran_gt)).scalar() or 0
        
        # Pelabuhan terpopuler
        pelabuhan_stats = db.session.query(
            Kapal.pelabuhan_pangkalan, 
            db.func.count(Kapal.id).label('count')
        ).group_by(Kapal.pelabuhan_pangkalan).order_by(db.text('count DESC')).limit(5).all()
        
        return {
            'total_kapal': total_kapal,
            'kapal_tangkap': kapal_tangkap,
            'kapal_budidaya': kapal_budidaya,
            'kapal_aktif': kapal_aktif,
            'kapal_nonaktif': total_kapal - kapal_aktif,
            'total_gt': round(total_gt, 2),
            'rata_rata_gt': round(total_gt / total_kapal, 2) if total_kapal > 0 else 0,
            'kapal_terbaru': [k.to_dict() for k in kapal_terbaru],
            'pelabuhan_stats': [{'pelabuhan': p[0], 'jumlah': p[1]} for p in pelabuhan_stats]
        }
        
    except Exception as e:
        print(f"[ERROR] Analytics error: {e}")
        return {
            'total_kapal': 0,
            'kapal_tangkap': 0,
            'kapal_budidaya': 0,
            'kapal_aktif': 0,
            'kapal_nonaktif': 0,
            'total_gt': 0,
            'rata_rata_gt': 0,
            'kapal_terbaru': [],
            'pelabuhan_stats': []
        }
