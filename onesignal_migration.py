#!/usr/bin/env python3
"""
OneSignal Database Migration Command
Bu komut production'da OneSignal kolonlarını otomatik ekler.
"""

import os
from flask import Flask
from models import db, User
from sqlalchemy import text

def create_app():
    """Flask app oluştur"""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Heroku/DigitalOcean PostgreSQL URL fix
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Local SQLite fallback
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/todo_company.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    
    db.init_app(app)
    return app

def migrate_onesignal_columns():
    """OneSignal kolonlarını veritabanına ekle"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Veritabanı bağlantısı test ediliyor...")
            
            # Database bağlantısını test et
            db.session.execute(text('SELECT 1'))
            print("✅ Veritabanı bağlantısı başarılı!")
            
            # OneSignal kolonlarını ekle
            columns_to_add = [
                ('push_notifications_enabled', 'BOOLEAN DEFAULT TRUE'),
                ('task_assignment_notifications', 'BOOLEAN DEFAULT TRUE'),
                ('task_completion_notifications', 'BOOLEAN DEFAULT TRUE'),
                ('reminder_notifications', 'BOOLEAN DEFAULT TRUE'),
                ('report_notifications', 'BOOLEAN DEFAULT TRUE'),
                ('onesignal_player_id', 'VARCHAR(255)')
            ]
            
            for column_name, column_def in columns_to_add:
                try:
                    # PostgreSQL için kolon ekleme
                    if 'postgresql' in str(db.engine.url):
                        sql = f'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS {column_name} {column_def}'
                    else:
                        # SQLite için
                        sql = f'ALTER TABLE user ADD COLUMN {column_name} {column_def}'
                    
                    db.session.execute(text(sql))
                    print(f"✅ Kolon eklendi/kontrol edildi: {column_name}")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e).lower():
                        print(f"ℹ️ Kolon zaten mevcut: {column_name}")
                    else:
                        print(f"⚠️ Kolon eklenemedi ({column_name}): {e}")
            
            # Değişiklikleri kaydet
            db.session.commit()
            
            print("\n🎉 OneSignal migration tamamlandı!")
            
            # Test sorgusu
            try:
                user = User.query.first()
                if user:
                    print(f"✅ Test başarılı - İlk kullanıcı: {user.username}")
                    print(f"📱 Push notifications: {getattr(user, 'push_notifications_enabled', 'N/A')}")
                else:
                    print("ℹ️ Veritabanında kullanıcı bulunamadı")
            except Exception as e:
                print(f"⚠️ Test sorgusu hatası: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration hatası: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = migrate_onesignal_columns()
    exit(0 if success else 1)