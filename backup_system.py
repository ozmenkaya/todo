#!/usr/bin/env python3
"""
Helmex Todo Yönetim Sistemi - Otomatik Yedekleme
PostgreSQL ve SQLite destekli yedekleme sistemi
"""

import os
import shutil
import sqlite3
import zipfile
import subprocess
from datetime import datetime
import schedule
import time
import logging

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

class TodoBackupManager:
    def __init__(self):
        # Veritabanı türünü belirle (PostgreSQL ya da SQLite)
        self.database_url = os.environ.get('DATABASE_URL')
        self.is_postgresql = self.database_url and 'postgresql' in self.database_url
        
        if self.is_postgresql:
            # PostgreSQL için pg_dump kullan
            self.backup_type = 'postgresql'
            logging.info("PostgreSQL yedekleme modu aktif")
        else:
            # SQLite için dosya kopyalama
            self.backup_type = 'sqlite'
            self.db_path = 'todo_company.db'
            logging.info("SQLite yedekleme modu aktif")
            
        self.backup_dir = 'backups'
        self.max_backups = 24 * 7  # 7 günlük saatlik yedek (168 dosya)
        
        # Backup dizinini oluştur
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logging.info(f"Backup dizini oluşturuldu: {self.backup_dir}")
    
    def create_backup(self):
        """Saatlik yedekleme işlemi"""
        try:
            # Timestamp ile dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.is_postgresql:
                return self._create_postgresql_backup(timestamp)
            else:
                return self._create_sqlite_backup(timestamp)
                
        except Exception as e:
            logging.error(f"❌ Yedekleme hatası: {e}")
            return False
    
    def _create_postgresql_backup(self, timestamp):
        """PostgreSQL için pg_dump yedekleme"""
        try:
            if not self.database_url:
                logging.error("DATABASE_URL bulunamadı")
                return False
                
            backup_filename = f"todo_backup_{timestamp}.sql"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # pg_dump komutu çalıştır
            cmd = [
                'pg_dump', 
                str(self.database_url),  # Ensure string type
                '--no-password', 
                '--verbose',
                '--file', backup_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logging.error(f"pg_dump hatası: {result.stderr}")
                return False
            
            # Gzip ile sıkıştır
            zip_path = backup_path.replace('.sql', '.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_filename)
            
            # Orijinal SQL dosyasını sil
            os.remove(backup_path)
            
            # Dosya boyutunu al
            file_size = os.path.getsize(zip_path)
            file_size_mb = file_size / (1024 * 1024)
            
            logging.info(f"✅ PostgreSQL yedekleme başarılı: {zip_path} ({file_size_mb:.2f} MB)")
            
            # Eski yedekleri temizle
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            logging.error(f"PostgreSQL yedekleme hatası: {e}")
            return False
    
    def _create_sqlite_backup(self, timestamp):
        """SQLite için optimize edilmiş yedekleme"""
        try:
            if not os.path.exists(self.db_path):
                logging.warning(f"Veritabanı dosyası bulunamadı: {self.db_path}")
                return False
            
            backup_filename = f"todo_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # SQLite VACUUM komutu ile optimize edilmiş yedek oluştur
            self._create_optimized_backup(backup_path)
            
            # Zip ile sıkıştır (opsiyonel)
            zip_path = backup_path.replace('.db', '.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_filename)
            
            # Orijinal .db dosyasını sil, sadece zip'i tut
            os.remove(backup_path)
            
            # Dosya boyutunu al
            file_size = os.path.getsize(zip_path)
            file_size_mb = file_size / (1024 * 1024)
            
            logging.info(f"✅ Yedekleme başarılı: {zip_path} ({file_size_mb:.2f} MB)")
            
            # Eski yedekleri temizle
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Yedekleme hatası: {e}")
            return False
    
    def _create_optimized_backup(self, backup_path):
        """VACUUM komutu ile optimize edilmiş yedek oluştur"""
        try:
            # Kaynak veritabanına bağlan
            source_conn = sqlite3.connect(self.db_path)
            
            # Hedef yedek dosyasına bağlan
            backup_conn = sqlite3.connect(backup_path)
            
            # Veritabanını yedekle
            source_conn.backup(backup_conn)
            
            # VACUUM ile optimize et
            backup_conn.execute('VACUUM')
            backup_conn.commit()
            
            # Bağlantıları kapat
            source_conn.close()
            backup_conn.close()
            
        except Exception as e:
            logging.error(f"Optimize edilmiş yedek oluşturma hatası: {e}")
            # Fallback: basit kopyalama
            shutil.copy2(self.db_path, backup_path)
    
    def _cleanup_old_backups(self):
        """Eski yedekleri temizle"""
        try:
            # Backup dizinindeki tüm zip dosyalarını listele
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('todo_backup_') and file.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Zamana göre sırala (en eski önce)
            backup_files.sort(key=lambda x: x[1])
            
            # Fazla dosyaları sil
            while len(backup_files) > self.max_backups:
                old_backup = backup_files.pop(0)
                os.remove(old_backup[0])
                logging.info(f"🗑️ Eski yedek silindi: {os.path.basename(old_backup[0])}")
                
        except Exception as e:
            logging.error(f"Eski yedek temizleme hatası: {e}")
    
    def get_backup_stats(self):
        """Yedekleme istatistikleri"""
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith('todo_backup_') and f.endswith('.zip')]
            
            if not backup_files:
                return {"count": 0, "total_size": 0, "latest": None}
            
            total_size = sum(os.path.getsize(os.path.join(self.backup_dir, f)) 
                           for f in backup_files)
            
            # En son yedek
            latest_file = max(backup_files, 
                            key=lambda f: os.path.getmtime(os.path.join(self.backup_dir, f)))
            latest_time = os.path.getmtime(os.path.join(self.backup_dir, latest_file))
            latest_datetime = datetime.fromtimestamp(latest_time)
            
            return {
                "count": len(backup_files),
                "total_size": total_size / (1024 * 1024),  # MB
                "latest": latest_datetime.strftime("%d.%m.%Y %H:%M:%S"),
                "latest_file": latest_file
            }
            
        except Exception as e:
            logging.error(f"İstatistik alma hatası: {e}")
            return {"count": 0, "total_size": 0, "latest": None}
    
    def restore_backup(self, backup_filename):
        """Yedekten geri yükleme"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                logging.error(f"Yedek dosyası bulunamadı: {backup_path}")
                return False
            
            # Mevcut veritabanını yedekle
            current_backup = f"current_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db_path, current_backup)
            
            # Zip dosyasından çıkart
            if backup_filename.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # İlk .db dosyasını bul
                    db_files = [f for f in zipf.namelist() if f.endswith('.db')]
                    if db_files:
                        zipf.extract(db_files[0])
                        shutil.move(db_files[0], self.db_path)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            logging.info(f"✅ Geri yükleme başarılı: {backup_filename}")
            logging.info(f"🔄 Mevcut veritabanı şu konuma yedeklendi: {current_backup}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Geri yükleme hatası: {e}")
            return False

def run_hourly_backup():
    """Saatlik yedekleme görevi"""
    backup_manager = TodoBackupManager()
    
    logging.info("🔄 Saatlik yedekleme başlatılıyor...")
    success = backup_manager.create_backup()
    
    if success:
        stats = backup_manager.get_backup_stats()
        logging.info(f"📊 Toplam yedek: {stats['count']} dosya, {stats['total_size']:.2f} MB")
    
    return success

def start_backup_scheduler():
    """Yedekleme zamanlayıcısını başlat"""
    logging.info("🚀 Helmex Todo Otomatik Yedekleme Sistemi başlatılıyor...")
    
    # Saatlik yedekleme planla
    schedule.every().hour.do(run_hourly_backup)
    
    # İlk yedeklemeyi hemen yap
    run_hourly_backup()
    
    logging.info("⏰ Saatlik yedekleme programlandı. Sistem çalışıyor...")
    logging.info("🛑 Durdurmak için Ctrl+C kullanın")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    except KeyboardInterrupt:
        logging.info("🛑 Yedekleme sistemi durduruldu")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Helmex Todo Yedekleme Sistemi')
    parser.add_argument('--start', action='store_true', help='Otomatik yedeklemeyi başlat')
    parser.add_argument('--backup', action='store_true', help='Tek seferlik yedek al')
    parser.add_argument('--stats', action='store_true', help='Yedekleme istatistikleri')
    parser.add_argument('--restore', type=str, help='Belirtilen yedekten geri yükle')
    
    args = parser.parse_args()
    
    backup_manager = TodoBackupManager()
    
    if args.start:
        start_backup_scheduler()
    elif args.backup:
        run_hourly_backup()
    elif args.stats:
        stats = backup_manager.get_backup_stats()
        print(f"📊 Yedekleme İstatistikleri:")
        print(f"   Toplam yedek: {stats['count']} dosya")
        print(f"   Toplam boyut: {stats['total_size']:.2f} MB")
        print(f"   Son yedek: {stats['latest'] or 'Henüz yedek alınmamış'}")
        if stats['latest_file']:
            print(f"   Son dosya: {stats['latest_file']}")
    elif args.restore:
        backup_manager.restore_backup(args.restore)
    else:
        print("Kullanım:")
        print("  python backup_system.py --start     # Otomatik yedeklemeyi başlat")
        print("  python backup_system.py --backup    # Tek seferlik yedek al")
        print("  python backup_system.py --stats     # İstatistikleri göster")
        print("  python backup_system.py --restore filename.zip  # Geri yükle")
