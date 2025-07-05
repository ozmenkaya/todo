#!/usr/bin/env python3
"""
Helmex Todo Yönetim Sistemi - Production Yedekleme Servisi
DigitalOcean App Platform için optimize edilmiş yedekleme sistemi
"""

import sys
import signal
import time
import logging
from datetime import datetime
from typing import Any
from backup_system import TodoBackupManager

# Logging konfigürasyonu - production için
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Stdout'a log gönder (DigitalOcean için)
        logging.FileHandler('backup_worker.log', mode='a')
    ]
)

class ProductionBackupWorker:
    """Production ortamı için yedekleme worker'ı"""
    
    def __init__(self):
        self.backup_manager = TodoBackupManager()
        self.running = True
        self.last_backup = None
        
        # Signal handler'ları kaydet
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logging.info("🚀 Helmex Backup Worker başlatıldı")
    
    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Graceful shutdown için signal handler"""
        logging.info(f"📡 Signal alındı ({signum}), güvenli şekilde durduruluyor...")
        self.running = False
    
    def run_backup_loop(self):
        """Ana yedekleme döngüsü"""
        # İlk yedeklemeyi hemen yap
        self._perform_backup()
        
        # Saatlik döngü
        last_hour = datetime.now().hour
        
        while self.running:
            try:
                current_hour = datetime.now().hour
                
                # Her saat başında yedek al
                if current_hour != last_hour:
                    self._perform_backup()
                    last_hour = current_hour
                
                # Health check log'u (her 10 dakikada bir)
                if datetime.now().minute % 10 == 0:
                    self._log_health_status()
                
                # 60 saniye bekle
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"❌ Worker döngüsünde hata: {e}")
                time.sleep(300)  # 5 dakika bekleyip devam et
        
        logging.info("🛑 Backup Worker durduruldu")
    
    def _perform_backup(self):
        """Yedekleme işlemini gerçekleştir"""
        try:
            logging.info("⏰ Saatlik yedekleme başlıyor...")
            success = self.backup_manager.create_backup()
            
            if success:
                self.last_backup = datetime.now()
                logging.info("✅ Saatlik yedekleme tamamlandı")
                
                # İstatistikleri log'la
                stats = self.backup_manager.get_backup_stats()
                logging.info(f"📊 Toplam yedek: {stats['count']}, Boyut: {stats['total_size']:.1f}MB")
            else:
                logging.error("❌ Yedekleme başarısız")
                
        except Exception as e:
            logging.error(f"❌ Yedekleme hatası: {e}")
    
    def _log_health_status(self) -> None:
        """Sistem sağlık durumunu logla"""
        last_backup_str = self.last_backup.strftime("%H:%M") if self.last_backup else "Henüz yok"
        logging.info(f"💚 Worker aktif - Son yedek: {last_backup_str}")

def main():
    """Ana fonksiyon"""
    worker = ProductionBackupWorker()
    
    try:
        logging.info("🔄 Yedekleme döngüsü başlıyor...")
        worker.run_backup_loop()
    except Exception as e:
        logging.error(f"💥 Worker kritik hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
