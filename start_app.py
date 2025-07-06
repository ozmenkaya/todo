#!/usr/bin/env python3
"""
Minimal Flask app starter - PostgreSQL hazır olana kadar SQLite kullan
"""

import os
import sys
import time
from app import app, db

def safe_start():
    """Güvenli app başlatma - database hazır olana kadar bekle"""
    
    print("🚀 Helmex Todo App başlatılıyor...")
    
    # Environment variables kontrol
    database_url = os.environ.get('DATABASE_URL')
    flask_env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5004))
    
    print(f"📊 Ortam: {flask_env}")
    print(f"📊 Port: {port}")
    print(f"📊 Database URL var mı: {'Evet' if database_url else 'Hayır'}")
    if database_url:
        # URL'i güvenli şekilde göster (şifre gizli)
        safe_url = database_url.split('@')[1] if '@' in database_url else database_url[:50]
        print(f"📊 Database: ...@{safe_url}")
    
    print(f"📊 Mail Server: {os.environ.get('MAIL_SERVER', 'Not set')}")
    print(f"📊 Mail Username: {os.environ.get('MAIL_USERNAME', 'Not set')}")
    
    # Flask app config check
    print(f"📊 Flask Config DB URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
    
    # Database initialization
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # PostgreSQL schema fix (ilk çalıştırmada)
            if database_url and 'postgresql' in database_url.lower() and attempt == 0:
                print("🛠️ PostgreSQL schema fix çalıştırılıyor...")
                try:
                    # Fix_postgresql_schema import ve çalıştırma
                    import sys
                    sys.path.append('.')
                    
                    from fix_postgresql_schema import fix_postgresql_schema
                    if fix_postgresql_schema():
                        print("✅ PostgreSQL schema fix başarılı")
                    else:
                        print("⚠️ PostgreSQL schema fix başarısız, normal başlatma devam ediyor")
                except ImportError as e:
                    print(f"⚠️ Schema fix import hatası: {e}")
                except Exception as e:
                    print(f"⚠️ Schema fix hatası: {e}")
            
            with app.app_context():
                print(f"⏳ Database bağlantısı test ediliyor... (deneme {attempt + 1})")
                
                # Basit tablo oluşturma testi
                db.create_all()
                print("✅ Database tabloları oluşturuldu")
                
                # Admin user check
                from app import create_admin_user
                create_admin_user()
                print("✅ Admin kullanıcı kontrolü tamamlandı")
                
                break
                
        except Exception as e:
            print(f"⚠️ Database hatası (deneme {attempt + 1}): {e}")
            
            if attempt < max_attempts - 1:
                print("⏳ 3 saniye bekleyip tekrar denenecek...")
                time.sleep(3)
            else:
                print("❌ Database başlatılamadı. App yine de başlatılacak...")
    
    # Flask app start
    debug = flask_env != 'production'
    print(f"🌐 Flask server başlatılıyor... Debug: {debug}")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"💥 Flask app başlatma hatası: {e}")
        sys.exit(1)

if __name__ == '__main__':
    safe_start()
