#!/usr/bin/env python3
"""
Production PostgreSQL Migration for OneSignal
Bu script production PostgreSQL veritabanında OneSignal kolonlarını ekler.
"""

import os
import sys
from flask import Flask
from models import db
import psycopg2
from urllib.parse import urlparse

def run_migration():
    """Production PostgreSQL'de OneSignal kolonlarını ekle"""
    
    # Database URL'ini al
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable bulunamadı!")
        return False
    
    print(f"🔍 PostgreSQL bağlantısı kontrol ediliyor...")
    
    try:
        # URL'yi parse et
        url = urlparse(database_url)
        
        # PostgreSQL bağlantısı
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],  # Remove leading slash
            user=url.username,
            password=url.password,
            sslmode='require'  # DigitalOcean için SSL gerekli
        )
        
        cursor = conn.cursor()
        
        # Mevcut kolonları kontrol et
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND table_schema = 'public'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Mevcut User tablosu kolonları: {existing_columns}")
        
        # Eklenecek kolonlar
        new_columns = [
            ('push_notifications_enabled', 'BOOLEAN DEFAULT TRUE'),
            ('task_assignment_notifications', 'BOOLEAN DEFAULT TRUE'),
            ('task_completion_notifications', 'BOOLEAN DEFAULT TRUE'),
            ('reminder_notifications', 'BOOLEAN DEFAULT TRUE'),
            ('report_notifications', 'BOOLEAN DEFAULT TRUE'),
            ('onesignal_player_id', 'VARCHAR(255)')
        ]
        
        # Her kolonu kontrol et ve eksik olanları ekle
        for column_name, column_definition in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE "user" ADD COLUMN {column_name} {column_definition}')
                    print(f"✅ Kolon eklendi: {column_name}")
                except Exception as e:
                    print(f"❌ Kolon eklenirken hata ({column_name}): {e}")
            else:
                print(f"ℹ️ Kolon zaten mevcut: {column_name}")
        
        # Değişiklikleri kaydet
        conn.commit()
        
        # Sonuçları kontrol et
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        updated_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Güncellenmiş User tablosu kolonları: {updated_columns}")
        
        cursor.close()
        conn.close()
        
        print("🎉 PostgreSQL migration tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL migration sırasında hata: {e}")
        return False

def main():
    """Ana migration fonksiyonu"""
    print("🚀 Production PostgreSQL OneSignal Migration")
    print("="*60)
    
    if run_migration():
        print("\n✅ Migration başarılı! OneSignal kolonları eklendi.")
        print("🔄 DigitalOcean app'i restart edin veya yeni deployment tetikleyin.")
        return 0
    else:
        print("\n❌ Migration başarısız!")
        return 1

if __name__ == "__main__":
    sys.exit(main())