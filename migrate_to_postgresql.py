#!/usr/bin/env python3
"""
DigitalOcean PostgreSQL database migration script
Bu script SQLite'dan PostgreSQL'e geçiş için kullanılır
"""

import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

def migrate_sqlite_to_postgresql():
    """SQLite verilerini PostgreSQL'e migrate eder"""
    
    # Environment variables
    database_url = os.environ.get('DATABASE_URL')
    sqlite_path = 'todo_company.db'
    
    if not database_url:
        print("❌ DATABASE_URL environment variable bulunamadı!")
        return False
        
    if not os.path.exists(sqlite_path):
        print("❌ SQLite database bulunamadı!")
        return False
    
    try:
        # PostgreSQL bağlantısı
        parsed = urlparse(database_url)
        pg_conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        pg_cursor = pg_conn.cursor()
        
        # SQLite bağlantısı
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        print("🔄 Migration başlıyor...")
        
        # Tables to migrate
        tables = ['user', 'task', 'task_assignments', 'comment', 'reminder']
        
        for table in tables:
            print(f"📦 {table} tablosu migrate ediliyor...")
            
            # SQLite'dan veri oku
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if rows:
                # Column names al
                sqlite_cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in sqlite_cursor.fetchall()]
                
                # PostgreSQL'e insert et
                placeholders = ','.join(['%s'] * len(columns))
                query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                
                pg_cursor.executemany(query, rows)
                print(f"✅ {len(rows)} satır migrate edildi")
            else:
                print(f"ℹ️ {table} tablosu boş")
        
        # Commit changes
        pg_conn.commit()
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print("🎉 Migration tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Migration hatası: {e}")
        return False

if __name__ == "__main__":
    migrate_sqlite_to_postgresql()
