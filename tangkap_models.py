# Models dan Functions khusus untuk Tangkap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json
from kapal_models import db, Kapal

class TripPenangkapan(db.Model):
    """
    Model untuk data trip penangkapan
    """
    __tablename__ = 'trip_penangkapan'
    
    id = db.Column(db.Integer, primary_key=True)
    kapal_id = db.Column(db.Integer, db.ForeignKey('kapal.id'), nullable=False)
    
    # Data Trip
    nomor_trip = db.Column(db.String(50), nullable=False)
    tanggal_berangkat = db.Column(db.DateTime, nullable=False)
    tanggal_kembali = db.Column(db.DateTime)
    status_trip = db.Column(db.String(20), default='berlangsung')  # berlangsung, selesai, batal
    
    # Data Operasional
    area_penangkapan = db.Column(db.String(100))
    koordinat_lat = db.Column(db.Float)
    koordinat_lon = db.Column(db.Float)
    kedalaman_air = db.Column(db.Float)  # meter
    
    # Data Cuaca
    kondisi_cuaca = db.Column(db.String(50))
    tinggi_gelombang = db.Column(db.Float)  # meter
    kecepatan_angin = db.Column(db.Float)   # knot
    
    # Data Bahan Bakar
    bbm_berangkat = db.Column(db.Float)     # liter
    bbm_kembali = db.Column(db.Float)       # liter
    konsumsi_bbm = db.Column(db.Float)      # liter
    
    # Data ABK
    jumlah_abk = db.Column(db.Integer, default=1)
    nama_nahkoda = db.Column(db.String(100))
    
    # Estimasi Biaya
    biaya_operasional = db.Column(db.Float)  # rupiah
    biaya_bbm = db.Column(db.Float)          # rupiah
    biaya_logistik = db.Column(db.Float)     # rupiah
    
    # Metadata
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    kapal = db.relationship('Kapal', backref=db.backref('trip_penangkapan', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'kapal_id': self.kapal_id,
            'nomor_trip': self.nomor_trip,
            'tanggal_berangkat': self.tanggal_berangkat.isoformat() if self.tanggal_berangkat else None,
            'tanggal_kembali': self.tanggal_kembali.isoformat() if self.tanggal_kembali else None,
            'status_trip': self.status_trip,
            'area_penangkapan': self.area_penangkapan,
            'koordinat_lat': self.koordinat_lat,
            'koordinat_lon': self.koordinat_lon,
            'kedalaman_air': self.kedalaman_air,
            'kondisi_cuaca': self.kondisi_cuaca,
            'tinggi_gelombang': self.tinggi_gelombang,
            'kecepatan_angin': self.kecepatan_angin,
            'bbm_berangkat': self.bbm_berangkat,
            'bbm_kembali': self.bbm_kembali,
            'konsumsi_bbm': self.konsumsi_bbm,
            'jumlah_abk': self.jumlah_abk,
            'nama_nahkoda': self.nama_nahkoda,
            'biaya_operasional': self.biaya_operasional,
            'biaya_bbm': self.biaya_bbm,
            'biaya_logistik': self.biaya_logistik,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HasilTangkapan(db.Model):
    """
    Model untuk data hasil tangkapan per trip
    """
    __tablename__ = 'hasil_tangkapan'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip_penangkapan.id'), nullable=False)
    
    # Data Ikan
    jenis_ikan = db.Column(db.String(50), nullable=False)
    berat_kg = db.Column(db.Float, nullable=False)
    jumlah_ekor = db.Column(db.Integer)
    ukuran_rata_rata = db.Column(db.Float)  # cm
    
    # Grade/Kualitas
    grade_a = db.Column(db.Float, default=0)  # kg
    grade_b = db.Column(db.Float, default=0)  # kg
    grade_c = db.Column(db.Float, default=0)  # kg
    
    # Harga dan Penjualan
    harga_per_kg = db.Column(db.Float)
    total_nilai = db.Column(db.Float)
    pembeli = db.Column(db.String(100))
    tempat_penjualan = db.Column(db.String(100))  # TPI, pengepul, dll
    
    # Alat Tangkap yang Digunakan
    alat_tangkap_utama = db.Column(db.String(50))
    lokasi_tangkap = db.Column(db.String(100))
    waktu_tangkap = db.Column(db.Time)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    trip = db.relationship('TripPenangkapan', backref=db.backref('hasil_tangkapan', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'jenis_ikan': self.jenis_ikan,
            'berat_kg': self.berat_kg,
            'jumlah_ekor': self.jumlah_ekor,
            'ukuran_rata_rata': self.ukuran_rata_rata,
            'grade_a': self.grade_a,
            'grade_b': self.grade_b,
            'grade_c': self.grade_c,
            'harga_per_kg': self.harga_per_kg,
            'total_nilai': self.total_nilai,
            'pembeli': self.pembeli,
            'tempat_penjualan': self.tempat_penjualan,
            'alat_tangkap_utama': self.alat_tangkap_utama,
            'lokasi_tangkap': self.lokasi_tangkap,
            'waktu_tangkap': self.waktu_tangkap.strftime('%H:%M:%S') if self.waktu_tangkap else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_tangkap_database(app):
    """
    Initialize tangkap database
    """
    with app.app_context():
        db.create_all()
        print("[OK] Tangkap database tables created!")
        
        # Create sample data if needed
        if TripPenangkapan.query.count() == 0:
            create_sample_tangkap_data()

def create_sample_tangkap_data():
    """
    Create sample data untuk tangkap
    """
    try:
        # Get tangkap kapal
        kapal_tangkap = Kapal.query.filter_by(jenis_kapal='tangkap').first()
        
        if kapal_tangkap:
            # Sample trip
            sample_trip = TripPenangkapan(
                kapal_id=kapal_tangkap.id,
                nomor_trip='TR-001-2024',
                tanggal_berangkat=datetime(2024, 3, 1, 4, 0),
                tanggal_kembali=datetime(2024, 3, 1, 16, 0),
                status_trip='selesai',
                area_penangkapan='Laut Jawa Utara',
                koordinat_lat=-5.8749,
                koordinat_lon=106.5173,
                kedalaman_air=25.0,
                kondisi_cuaca='cerah',
                tinggi_gelombang=0.5,
                kecepatan_angin=8.0,
                bbm_berangkat=200.0,
                bbm_kembali=50.0,
                konsumsi_bbm=150.0,
                jumlah_abk=4,
                nama_nahkoda='Pak Budi',
                biaya_operasional=500000,
                biaya_bbm=900000,
                biaya_logistik=200000,
                created_by='user_tangkap'
            )
            
            db.session.add(sample_trip)
            db.session.commit()
            
            # Sample hasil tangkapan
            sample_hasil = [
                {
                    'trip_id': sample_trip.id,
                    'jenis_ikan': 'Ikan Tongkol',
                    'berat_kg': 45.5,
                    'jumlah_ekor': 25,
                    'ukuran_rata_rata': 28.0,
                    'grade_a': 30.0,
                    'grade_b': 12.0,
                    'grade_c': 3.5,
                    'harga_per_kg': 35000,
                    'total_nilai': 1592500,
                    'pembeli': 'TPI Muara Angke',
                    'tempat_penjualan': 'TPI',
                    'alat_tangkap_utama': 'Jaring Insang',
                    'lokasi_tangkap': 'Perairan Karawang'
                },
                {
                    'trip_id': sample_trip.id,
                    'jenis_ikan': 'Ikan Kembung',
                    'berat_kg': 22.0,
                    'jumlah_ekor': 80,
                    'ukuran_rata_rata': 18.0,
                    'grade_a': 15.0,
                    'grade_b': 7.0,
                    'grade_c': 0.0,
                    'harga_per_kg': 25000,
                    'total_nilai': 550000,
                    'pembeli': 'Pengepul Lokal',
                    'tempat_penjualan': 'Pengepul',
                    'alat_tangkap_utama': 'Jaring Insang',
                    'lokasi_tangkap': 'Perairan Bekasi'
                }
            ]
            
            for hasil_data in sample_hasil:
                hasil = HasilTangkapan(**hasil_data)
                db.session.add(hasil)
            
            db.session.commit()
            print("[OK] Sample tangkap data created!")
    
    except Exception as e:
        print(f"[ERROR] Creating sample tangkap data: {e}")
        db.session.rollback()

def get_tangkap_analytics(username=None):
    """
    Get analytics khusus untuk tangkap
    """
    try:
        # Filter by user if provided
        if username:
            kapal_tangkap = Kapal.query.filter_by(
                jenis_kapal='tangkap', 
                registered_by=username
            ).all()
        else:
            kapal_tangkap = Kapal.query.filter_by(jenis_kapal='tangkap').all()
        
        # Basic stats
        total_kapal = len(kapal_tangkap)
        kapal_aktif = len([k for k in kapal_tangkap if k.status_registrasi == 'aktif'])
        
        # Trip stats
        total_trip = TripPenangkapan.query.join(Kapal).filter(
            Kapal.jenis_kapal == 'tangkap'
        ).count() if not username else TripPenangkapan.query.join(Kapal).filter(
            Kapal.registered_by == username
        ).count()
        
        trip_aktif = TripPenangkapan.query.join(Kapal).filter(
            TripPenangkapan.status_trip == 'berlangsung',
            Kapal.jenis_kapal == 'tangkap'
        ).count() if not username else TripPenangkapan.query.join(Kapal).filter(
            TripPenangkapan.status_trip == 'berlangsung',
            Kapal.registered_by == username
        ).count()
        
        # Hasil tangkapan stats
        total_tangkapan = db.session.query(db.func.sum(HasilTangkapan.berat_kg)).join(
            TripPenangkapan).join(Kapal).filter(
            Kapal.jenis_kapal == 'tangkap'
        ).scalar() or 0
        
        total_nilai = db.session.query(db.func.sum(HasilTangkapan.total_nilai)).join(
            TripPenangkapan).join(Kapal).filter(
            Kapal.jenis_kapal == 'tangkap'
        ).scalar() or 0
        
        # BBM stats
        total_bbm = db.session.query(db.func.sum(TripPenangkapan.konsumsi_bbm)).join(Kapal).filter(
            Kapal.jenis_kapal == 'tangkap'
        ).scalar() or 0
        
        # Ikan populer
        ikan_populer = db.session.query(
            HasilTangkapan.jenis_ikan,
            db.func.sum(HasilTangkapan.berat_kg).label('total_berat')
        ).join(TripPenangkapan).join(Kapal).filter(
            Kapal.jenis_kapal == 'tangkap'
        ).group_by(HasilTangkapan.jenis_ikan).order_by(db.text('total_berat DESC')).limit(5).all()
        
        # Area penangkapan
        area_stats = db.session.query(
            TripPenangkapan.area_penangkapan,
            db.func.count(TripPenangkapan.id).label('count')
        ).join(Kapal).filter(
            Kapal.jenis_kapal == 'tangkap'
        ).group_by(TripPenangkapan.area_penangkapan).order_by(db.text('count DESC')).limit(5).all()
        
        return {
            'total_kapal': total_kapal,
            'kapal_aktif': kapal_aktif,
            'total_trip': total_trip,
            'trip_aktif': trip_aktif,
            'total_tangkapan': round(total_tangkapan, 1),
            'total_nilai': round(total_nilai / 1000000, 1),  # dalam juta
            'rata_per_trip': round(total_tangkapan / total_trip, 1) if total_trip > 0 else 0,
            'total_bbm': round(total_bbm, 1),
            'efisiensi_bbm': round(total_tangkapan / total_bbm, 2) if total_bbm > 0 else 0,
            'ikan_populer': [
                {'jenis': i[0] or 'Tidak diset', 'berat': round(i[1], 1)} 
                for i in ikan_populer
            ],
            'area_stats': [
                {'area': a[0] or 'Tidak diset', 'jumlah': a[1]} 
                for a in area_stats
            ],
            'target_bulan_ini': {
                'trip': 15,
                'tangkapan': 85.5,  # ton
                'pendapatan': 425.0  # juta
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Tangkap analytics: {e}")
        return {
            'total_kapal': 0,
            'kapal_aktif': 0,
            'total_trip': 0,
            'trip_aktif': 0,
            'total_tangkapan': 0,
            'total_nilai': 0,
            'rata_per_trip': 0,
            'total_bbm': 0,
            'efisiensi_bbm': 0,
            'ikan_populer': [],
            'area_stats': [],
            'target_bulan_ini': {
                'trip': 0,
                'tangkapan': 0,
                'pendapatan': 0
            }
        }
