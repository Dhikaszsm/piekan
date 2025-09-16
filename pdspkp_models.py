# Models dan Functions khusus untuk PDSPKP (Mutu Produk Perikanan)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json
from kapal_models import db

class PermohonanSertifikasiProduk(db.Model):
    """
    Model untuk permohonan sertifikasi produk perikanan (GMP/SKP)
    """
    __tablename__ = 'permohonan_sertifikasi_produk'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Data Permohonan
    nomor_permohonan = db.Column(db.String(50), unique=True, nullable=False)
    tanggal_permohonan = db.Column(db.Date, nullable=False)
    nomor_surat = db.Column(db.String(50))
    
    # Data Perusahaan
    nama_pt = db.Column(db.String(200), nullable=False)
    alamat_pt = db.Column(db.Text, nullable=False)
    wilayah_dki = db.Column(db.String(50))  # Jakarta Timur, Barat, Selatan, Utara, Kepulauan Seribu
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telepon = db.Column(db.String(20))
    
    # Data Produk
    jenis_produk = db.Column(db.String(100), nullable=False)  # ikan segar, olahan, frozen, dll
    nama_produk = db.Column(db.String(200))
    spesifikasi_produk = db.Column(db.Text)
    jenis_sertifikat = db.Column(db.String(20), nullable=False)  # GMP, SKP
    tujuan_export = db.Column(db.String(100))  # negara tujuan export
    
    # Data Surat Tugas
    nomor_surat_tugas = db.Column(db.String(50))
    tanggal_surat_tugas = db.Column(db.Date)
    
    # Data Rekomendasi Teknis
    nomor_rekomtek = db.Column(db.String(50))
    tanggal_rekomtek = db.Column(db.Date)
    
    # Data Kunjungan
    anggota_kunjungan = db.Column(db.Text)  # JSON array
    tanggal_kunjungan = db.Column(db.Date)
    
    # Data Sertifikasi
    periode_tahun_sertifikasi = db.Column(db.Integer)
    status_permohonan = db.Column(db.String(20), default='dalam_proses')  # dalam_proses, diterbitkan, ditolak
    
    # Hasil Audit
    hasil_audit = db.Column(db.Text)  # JSON hasil audit
    score_audit = db.Column(db.Float)  # 0-100
    catatan_auditor = db.Column(db.Text)
    rekomendasi = db.Column(db.String(20))  # disetujui, ditolak, perbaikan
    
    # Data Sertifikat (jika disetujui)
    nomor_sertifikat = db.Column(db.String(50))
    tanggal_terbit_sertifikat = db.Column(db.Date)
    masa_berlaku_sertifikat = db.Column(db.Date)
    
    # Biaya
    biaya_sertifikasi = db.Column(db.Float)
    biaya_audit = db.Column(db.Float)
    total_biaya = db.Column(db.Float)
    
    # Metadata
    created_by = db.Column(db.String(50))  # PDSPKP officer
    processed_by = db.Column(db.String(50))  # Auditor
    approved_by = db.Column(db.String(50))  # Kepala PDSPKP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_anggota_kunjungan(self, anggota_list):
        """Set anggota kunjungan sebagai JSON array"""
        self.anggota_kunjungan = json.dumps(anggota_list)
    
    def get_anggota_kunjungan(self):
        """Get anggota kunjungan sebagai list"""
        if self.anggota_kunjungan:
            try:
                return json.loads(self.anggota_kunjungan)
            except:
                return []
        return []
    
    def set_hasil_audit(self, hasil_dict):
        """Set hasil audit sebagai JSON"""
        self.hasil_audit = json.dumps(hasil_dict)
    
    def get_hasil_audit(self):
        """Get hasil audit sebagai dict"""
        if self.hasil_audit:
            try:
                return json.loads(self.hasil_audit)
            except:
                return {}
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'nomor_permohonan': self.nomor_permohonan,
            'tanggal_permohonan': self.tanggal_permohonan.isoformat() if self.tanggal_permohonan else None,
            'nomor_surat': self.nomor_surat,
            'nama_pt': self.nama_pt,
            'alamat_pt': self.alamat_pt,
            'contact_person': self.contact_person,
            'email': self.email,
            'telepon': self.telepon,
            'jenis_produk': self.jenis_produk,
            'nama_produk': self.nama_produk,
            'spesifikasi_produk': self.spesifikasi_produk,
            'jenis_sertifikat': self.jenis_sertifikat,
            'tujuan_export': self.tujuan_export,
            'nomor_surat_tugas': self.nomor_surat_tugas,
            'tanggal_surat_tugas': self.tanggal_surat_tugas.isoformat() if self.tanggal_surat_tugas else None,
            'nomor_rekomtek': self.nomor_rekomtek,
            'tanggal_rekomtek': self.tanggal_rekomtek.isoformat() if self.tanggal_rekomtek else None,
            'anggota_kunjungan': self.get_anggota_kunjungan(),
            'tanggal_kunjungan': self.tanggal_kunjungan.isoformat() if self.tanggal_kunjungan else None,
            'periode_tahun_sertifikasi': self.periode_tahun_sertifikasi,
            'status_permohonan': self.status_permohonan,
            'hasil_audit': self.get_hasil_audit(),
            'score_audit': self.score_audit,
            'catatan_auditor': self.catatan_auditor,
            'rekomendasi': self.rekomendasi,
            'nomor_sertifikat': self.nomor_sertifikat,
            'tanggal_terbit_sertifikat': self.tanggal_terbit_sertifikat.isoformat() if self.tanggal_terbit_sertifikat else None,
            'masa_berlaku_sertifikat': self.masa_berlaku_sertifikat.isoformat() if self.masa_berlaku_sertifikat else None,
            'biaya_sertifikasi': self.biaya_sertifikasi,
            'biaya_audit': self.biaya_audit,
            'total_biaya': self.total_biaya,
            'created_by': self.created_by,
            'processed_by': self.processed_by,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PermohonanSertifikasiProduk {self.nomor_permohonan}: {self.nama_pt} - {self.jenis_produk}>'

class LaporanMonitoringMutu(db.Model):
    """
    Model untuk laporan monitoring mutu di lingkup pengolah (pasar, mall, modern market)
    """
    __tablename__ = 'laporan_monitoring_mutu'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Data Laporan
    nomor_laporan = db.Column(db.String(50), unique=True, nullable=False)
    tanggal_monitoring = db.Column(db.Date, nullable=False)
    periode_bulan = db.Column(db.Integer)  # 1-12
    periode_tahun = db.Column(db.Integer)
    
    # Data Lokasi
    nama_lokasi = db.Column(db.String(200), nullable=False)  # nama pasar/mall
    alamat_lokasi = db.Column(db.Text)
    wilayah_dki = db.Column(db.String(50))  # Jakarta Timur, Barat, Selatan, Utara, Kepulauan Seribu
    jenis_lokasi = db.Column(db.String(50))  # pasar tradisional, mall, modern market, supermarket
    kategori_pengolah = db.Column(db.String(50))  # retail, grosir, pengolah
    
    # Data Monitoring
    jumlah_outlet = db.Column(db.Integer)  # jumlah toko/outlet yang dimonitor
    jumlah_sampel = db.Column(db.Integer)  # jumlah produk yang disampling
    
    # Temuan Monitoring
    produk_aman = db.Column(db.Integer, default=0)
    produk_tidak_aman = db.Column(db.Integer, default=0)
    produk_kadaluwarsa = db.Column(db.Integer, default=0)
    produk_tanpa_label = db.Column(db.Integer, default=0)
    
    # Jenis Produk yang Dimonitor
    produk_ikan_segar = db.Column(db.Integer, default=0)
    produk_ikan_olahan = db.Column(db.Integer, default=0)
    produk_ikan_frozen = db.Column(db.Integer, default=0)
    produk_ikan_kaleng = db.Column(db.Integer, default=0)
    produk_udang = db.Column(db.Integer, default=0)
    produk_lainnya = db.Column(db.Integer, default=0)
    
    # Asal Produk (untuk analisis export/import)
    produk_lokal = db.Column(db.Integer, default=0)
    produk_import = db.Column(db.Integer, default=0)
    negara_asal_import = db.Column(db.Text)  # JSON array
    
    # Tingkat Kepatuhan
    tingkat_kepatuhan = db.Column(db.Float)  # persen
    skor_higienitas = db.Column(db.Float)    # 0-100
    skor_pelabelan = db.Column(db.Float)     # 0-100
    
    # Tindakan
    tindakan_diambil = db.Column(db.Text)
    sanksi_diberikan = db.Column(db.Text)
    
    # Metadata
    petugas_monitoring = db.Column(db.String(100))
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_negara_asal_import(self, negara_list):
        """Set negara asal import sebagai JSON array"""
        self.negara_asal_import = json.dumps(negara_list)
    
    def get_negara_asal_import(self):
        """Get negara asal import sebagai list"""
        if self.negara_asal_import:
            try:
                return json.loads(self.negara_asal_import)
            except:
                return []
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'nomor_laporan': self.nomor_laporan,
            'tanggal_monitoring': self.tanggal_monitoring.isoformat() if self.tanggal_monitoring else None,
            'periode_bulan': self.periode_bulan,
            'periode_tahun': self.periode_tahun,
            'nama_lokasi': self.nama_lokasi,
            'alamat_lokasi': self.alamat_lokasi,
            'jenis_lokasi': self.jenis_lokasi,
            'kategori_pengolah': self.kategori_pengolah,
            'jumlah_outlet': self.jumlah_outlet,
            'jumlah_sampel': self.jumlah_sampel,
            'produk_aman': self.produk_aman,
            'produk_tidak_aman': self.produk_tidak_aman,
            'produk_kadaluwarsa': self.produk_kadaluwarsa,
            'produk_tanpa_label': self.produk_tanpa_label,
            'produk_ikan_segar': self.produk_ikan_segar,
            'produk_ikan_olahan': self.produk_ikan_olahan,
            'produk_ikan_frozen': self.produk_ikan_frozen,
            'produk_ikan_kaleng': self.produk_ikan_kaleng,
            'produk_udang': self.produk_udang,
            'produk_lainnya': self.produk_lainnya,
            'produk_lokal': self.produk_lokal,
            'produk_import': self.produk_import,
            'negara_asal_import': self.get_negara_asal_import(),
            'tingkat_kepatuhan': self.tingkat_kepatuhan,
            'skor_higienitas': self.skor_higienitas,
            'skor_pelabelan': self.skor_pelabelan,
            'tindakan_diambil': self.tindakan_diambil,
            'sanksi_diberikan': self.sanksi_diberikan,
            'petugas_monitoring': self.petugas_monitoring,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_pdspkp_database(app):
    """
    Initialize PDSPKP database untuk mutu produk
    """
    with app.app_context():
        db.create_all()
        print("[OK] PDSPKP Mutu database tables created!")
        
        # Create sample data if needed
        if PermohonanSertifikasiProduk.query.count() == 0:
            create_sample_pdspkp_mutu_data()

def create_sample_pdspkp_mutu_data():
    """
    Create sample data untuk PDSPKP mutu
    """
    try:
        # Sample permohonan sertifikasi
        sample_permohonan = [
            {
                'nomor_permohonan': 'SKP-001-2024',
                'tanggal_permohonan': date(2024, 2, 1),
                'nomor_surat': 'SRT-001/2024',
                'nama_pt': 'PT Bahari Mandiri Sejahtera',
                'alamat_pt': 'Jl. Pelabuhan Raya No. 123, Jakarta Utara',
                'contact_person': 'Budi Hartono',
                'email': 'budi@baharimandiri.com',
                'telepon': '021-5551234',
                'jenis_produk': 'Ikan Frozen',
                'nama_produk': 'Frozen Tuna Loin',
                'jenis_sertifikat': 'SKP',
                'tujuan_export': 'Jepang',
                'nomor_surat_tugas': 'ST-001/2024',
                'tanggal_surat_tugas': date(2024, 2, 5),
                'nomor_rekomtek': 'RT-001/2024',
                'tanggal_rekomtek': date(2024, 2, 10),
                'tanggal_kunjungan': date(2024, 2, 15),
                'periode_tahun_sertifikasi': 2024,
                'status_permohonan': 'diterbitkan',
                'score_audit': 92.5,
                'rekomendasi': 'disetujui',
                'nomor_sertifikat': 'CERT-SKP-001-2024',
                'tanggal_terbit_sertifikat': date(2024, 3, 1),
                'masa_berlaku_sertifikat': date(2025, 3, 1),
                'biaya_sertifikasi': 2500000,
                'biaya_audit': 1500000,
                'total_biaya': 4000000,
                'created_by': 'sari_pds'
            },
            {
                'nomor_permohonan': 'GMP-002-2024',
                'tanggal_permohonan': date(2024, 2, 15),
                'nomor_surat': 'SRT-002/2024',
                'nama_pt': 'CV Samudra Raya Foods',
                'alamat_pt': 'Jl. Industri No. 45, Bekasi',
                'contact_person': 'Sari Dewi',
                'email': 'sari@samudraraya.com',
                'telepon': '021-8881234',
                'jenis_produk': 'Ikan Olahan',
                'nama_produk': 'Abon Ikan Tuna',
                'jenis_sertifikat': 'GMP',
                'nomor_surat_tugas': 'ST-002/2024',
                'tanggal_surat_tugas': date(2024, 2, 20),
                'nomor_rekomtek': 'RT-002/2024',
                'tanggal_rekomtek': date(2024, 2, 25),
                'tanggal_kunjungan': date(2024, 3, 1),
                'periode_tahun_sertifikasi': 2024,
                'status_permohonan': 'dalam_proses',
                'created_by': 'dewi_pds'
            },
            {
                'nomor_permohonan': 'SKP-003-2024',
                'tanggal_permohonan': date(2024, 1, 10),
                'nomor_surat': 'SRT-003/2024',
                'nama_pt': 'PT Nusantara Fishery',
                'alamat_pt': 'Jl. Raya Pantai No. 78, Surabaya',
                'contact_person': 'Ahmad Fauzi',
                'email': 'ahmad@nusantarafishery.co.id',
                'telepon': '031-7771234',
                'jenis_produk': 'Udang Frozen',
                'nama_produk': 'Frozen Vannamei Shrimp',
                'jenis_sertifikat': 'SKP',
                'tujuan_export': 'Amerika Serikat',
                'periode_tahun_sertifikasi': 2024,
                'status_permohonan': 'ditolak',
                'rekomendasi': 'ditolak',
                'catatan_auditor': 'Fasilitas produksi belum memenuhi standar HACCP',
                'created_by': 'rina_pds'
            }
        ]
        
        for permohonan_data in sample_permohonan:
            # Set anggota kunjungan sample
            anggota = ['Auditor Senior', 'Inspektur Mutu', 'Teknisi Lab']
            
            permohonan = PermohonanSertifikasiProduk(**permohonan_data)
            permohonan.set_anggota_kunjungan(anggota)
            
            # Set hasil audit sample untuk yang sudah selesai
            if permohonan.status_permohonan == 'diterbitkan':
                hasil_audit = {
                    'sanitasi': 95,
                    'haccp': 90,
                    'dokumentasi': 88,
                    'fasilitas': 92,
                    'sumber_daya': 89
                }
                permohonan.set_hasil_audit(hasil_audit)
            
            db.session.add(permohonan)
        
        # Sample monitoring data
        sample_monitoring = [
            {
                'nomor_laporan': 'MON-001-2024',
                'tanggal_monitoring': date(2024, 3, 1),
                'periode_bulan': 3,
                'periode_tahun': 2024,
                'nama_lokasi': 'Pasar Ikan Modern Muara Karang',
                'alamat_lokasi': 'Jl. Pluit Karang Ayu, Jakarta Utara',
                'jenis_lokasi': 'pasar modern',
                'kategori_pengolah': 'retail',
                'jumlah_outlet': 25,
                'jumlah_sampel': 150,
                'produk_aman': 135,
                'produk_tidak_aman': 8,
                'produk_kadaluwarsa': 5,
                'produk_tanpa_label': 2,
                'produk_ikan_segar': 60,
                'produk_ikan_olahan': 40,
                'produk_ikan_frozen': 30,
                'produk_ikan_kaleng': 15,
                'produk_udang': 5,
                'produk_lokal': 120,
                'produk_import': 30,
                'tingkat_kepatuhan': 90.0,
                'skor_higienitas': 85.5,
                'skor_pelabelan': 88.0,
                'petugas_monitoring': 'Tim Monitoring PDSPKP',
                'created_by': 'sari_pds'
            }
        ]
        
        for monitoring_data in sample_monitoring:
            monitoring = LaporanMonitoringMutu(**monitoring_data)
            monitoring.set_negara_asal_import(['Thailand', 'Vietnam', 'China'])
            db.session.add(monitoring)
        
        db.session.commit()
        print("[OK] Sample PDSPKP mutu data created!")
    
    except Exception as e:
        print(f"[ERROR] Creating sample PDSPKP mutu data: {e}")
        db.session.rollback()

def get_pdspkp_analytics(username=None):
    """
    Get analytics khusus untuk PDSPKP mutu produk
    """
    try:
        # 4 Data Penting untuk Dashboard
        total_permintaan = PermohonanSertifikasiProduk.query.count()
        sertifikasi_diterbitkan = PermohonanSertifikasiProduk.query.filter_by(status_permohonan='diterbitkan').count()
        dalam_proses = PermohonanSertifikasiProduk.query.filter_by(status_permohonan='dalam_proses').count()
        ditolak = PermohonanSertifikasiProduk.query.filter_by(status_permohonan='ditolak').count()
        
        # Jenis sertifikat stats
        skp_count = PermohonanSertifikasiProduk.query.filter_by(jenis_sertifikat='SKP').count()
        gmp_count = PermohonanSertifikasiProduk.query.filter_by(jenis_sertifikat='GMP').count()
        
        # Analisis produk export/import
        produk_export_stats = db.session.query(
            PermohonanSertifikasiProduk.jenis_produk,
            db.func.count(PermohonanSertifikasiProduk.id).label('count')
        ).filter(
            PermohonanSertifikasiProduk.jenis_sertifikat == 'SKP'
        ).group_by(PermohonanSertifikasiProduk.jenis_produk).order_by(db.text('count DESC')).limit(5).all()
        
        # Kategori pengolah stats dari monitoring
        kategori_pengolah_stats = db.session.query(
            LaporanMonitoringMutu.kategori_pengolah,
            db.func.count(LaporanMonitoringMutu.id).label('count')
        ).group_by(LaporanMonitoringMutu.kategori_pengolah).order_by(db.text('count DESC')).all()
        
        # Revenue dan performance
        total_revenue = db.session.query(db.func.sum(PermohonanSertifikasiProduk.total_biaya)).scalar() or 0
        avg_score = db.session.query(db.func.avg(PermohonanSertifikasiProduk.score_audit)).scalar() or 0
        
        # Approval rate
        approval_rate = (sertifikasi_diterbitkan / total_permintaan * 100) if total_permintaan > 0 else 0
        
        return {
            # 4 Data Penting Dashboard
            'total_permintaan': total_permintaan,
            'sertifikasi_diterbitkan': sertifikasi_diterbitkan,
            'dalam_proses': dalam_proses,
            'ditolak': ditolak,
            
            # Jenis Sertifikat
            'skp_count': skp_count,
            'gmp_count': gmp_count,
            
            # Performance Metrics
            'approval_rate': round(approval_rate, 1),
            'avg_score': round(avg_score, 1),
            'total_revenue': round(total_revenue / 1000000, 1),  # dalam juta
            
            # Analytics Export/Import
            'produk_export_populer': [
                {'produk': p[0], 'jumlah': p[1]} 
                for p in produk_export_stats
            ],
            
            # Kategori Pengolah
            'kategori_pengolah_stats': [
                {'kategori': k[0] or 'Tidak diset', 'jumlah': k[1]} 
                for k in kategori_pengolah_stats
            ],
            
            # Target
            'target_bulan_ini': {
                'permohonan_baru': 15,
                'sertifikat_terbit': 12,
                'monitoring': 8,
                'revenue': 45.0  # juta
            }
        }
        
    except Exception as e:
        print(f"[ERROR] PDSPKP mutu analytics: {e}")
        return {
            'total_permintaan': 0,
            'sertifikasi_diterbitkan': 0,
            'dalam_proses': 0,
            'ditolak': 0,
            'skp_count': 0,
            'gmp_count': 0,
            'approval_rate': 0,
            'avg_score': 0,
            'total_revenue': 0,
            'produk_export_populer': [],
            'kategori_pengolah_stats': [],
            'target_bulan_ini': {
                'permohonan_baru': 0,
                'sertifikat_terbit': 0,
                'monitoring': 0,
                'revenue': 0
            }
        }
