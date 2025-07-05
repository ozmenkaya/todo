#!/usr/bin/env python3
"""
Safe backup worker starter
"""

import os
import sys
import time
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def start_backup_worker():
    """Güvenli backup worker başlatma"""
    
    print("🔄 Backup Worker başlatılıyor...")
    
    # Environment check
    database_url = os.environ.get('DATABASE_URL')
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    print(f"📊 Ortam: {flask_env}")
    print(f"📊 Database URL var mı: {'Evet' if database_url else 'Hayır'}")
    
    # Web servisinin başlamasını bekle
    print("⏳ Web servisinin başlamasını bekliyoruz...")
    time.sleep(30)  # 30 saniye bekle
    
    try:
        from backup_worker import ProductionBackupWorker
        
        worker = ProductionBackupWorker()
        worker.run_backup_loop()
        
    except ImportError as e:
        print(f"❌ Backup module import hatası: {e}")
        print("⏳ Backup sistemi devre dışı, sadece log çıkarılacak...")
        
        # Fallback: Sadece health log
        while True:
            print("💚 Backup worker aktif (backup sistemi devre dışı)")
            time.sleep(300)  # 5 dakikada bir log
            
    except Exception as e:
        print(f"💥 Backup worker genel hatası: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_backup_worker()
