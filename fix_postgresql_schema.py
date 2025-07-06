#!/usr/bin/env python3
"""
PostgreSQL Schema Fix - Karakter limiti sorunlarını çöz
"""

import os
import sys
from sqlalchemy import create_engine, text

def fix_postgresql_schema():
    """PostgreSQL şemasını düzelt - karakter limitlerini artır"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL bulunamadı")
        return False
    
    try:
        engine = create_engine(database_url)
        
        print("🔄 PostgreSQL şema düzeltmeleri başlıyor...")
        
        with engine.connect() as conn:
            # Transaction başlat
            trans = conn.begin()
            
            try:
                # Tabloları sil (foreign key constraints ile birlikte)
                print("🗑️ Mevcut tabloları siliniyor...")
                conn.execute(text("DROP TABLE IF EXISTS task_assignments CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS comment CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS reminder CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS task CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS user CASCADE"))
                
                print("✅ Mevcut tablolar silindi")
                
                # Yeni tablolar oluştur (düzeltilmiş karakter limitleri ile)
                print("🔧 Yeni tablolar oluşturuluyor...")
                
                # User table
                conn.execute(text("""
                    CREATE TABLE "user" (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) DEFAULT 'employee',
                        department VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Task table
                conn.execute(text("""
                    CREATE TABLE task (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        priority VARCHAR(10) DEFAULT 'medium',
                        due_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        created_by INTEGER NOT NULL REFERENCES "user"(id)
                    )
                """))
                
                # Task assignments (Many-to-Many)
                conn.execute(text("""
                    CREATE TABLE task_assignments (
                        task_id INTEGER REFERENCES task(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
                        PRIMARY KEY (task_id, user_id)
                    )
                """))
                
                # Reminder table
                conn.execute(text("""
                    CREATE TABLE reminder (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        description TEXT,
                        reminder_date TIMESTAMP NOT NULL,
                        is_completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL REFERENCES "user"(id)
                    )
                """))
                
                # Comment table
                conn.execute(text("""
                    CREATE TABLE comment (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        task_id INTEGER NOT NULL REFERENCES task(id),
                        user_id INTEGER NOT NULL REFERENCES "user"(id)
                    )
                """))
                
                print("✅ Yeni tablolar oluşturuldu")
                
                # Admin kullanıcı ekle
                print("👤 Admin kullanıcı oluşturuluyor...")
                from werkzeug.security import generate_password_hash
                
                admin_hash = generate_password_hash('admin123')
                conn.execute(text("""
                    INSERT INTO "user" (username, email, password_hash, role, department)
                    VALUES ('admin', 'admin@helmex.com.tr', :password_hash, 'admin', 'IT')
                """), {"password_hash": admin_hash})
                
                print("✅ Admin kullanıcı oluşturuldu")
                
                # Transaction commit
                trans.commit()
                print("🎉 PostgreSQL şema düzeltmesi tamamlandı!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Transaction rollback: {e}")
                return False
                
    except Exception as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        return False

if __name__ == "__main__":
    print("🛠️ PostgreSQL Schema Fix başlatılıyor...")
    success = fix_postgresql_schema()
    
    if success:
        print("✅ Schema düzeltmesi başarılı!")
        sys.exit(0)
    else:
        print("❌ Schema düzeltmesi başarısız!")
        sys.exit(1)
