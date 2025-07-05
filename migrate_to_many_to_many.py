#!/usr/bin/env python3
"""
Veritabanını Many-to-Many yapısına geçiş için migration scripti
"""

import os
import sqlite3
from datetime import datetime

def backup_database():
    """Mevcut veritabanını yedekle"""
    if os.path.exists('todo_company.db'):
        backup_name = f'todo_company_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy2('todo_company.db', backup_name)
        print(f"✓ Veritabanı yedeklendi: {backup_name}")
        return backup_name
    return None

def migrate_database():
    """Veritabanını Many-to-Many yapısına geçir"""
    
    # Önce yedek al
    backup_database()
    
    # Veritabanına bağlan
    conn = sqlite3.connect('todo_company.db')
    cursor = conn.cursor()
    
    try:
        # Önce task_assignments tablosunu oluştur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_assignments (
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, user_id),
                FOREIGN KEY (task_id) REFERENCES task (id),
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✓ task_assignments tablosu oluşturuldu")
        
        # Mevcut görevlerdeki assigned_to verilerini task_assignments'a kopyala
        cursor.execute('SELECT id, assigned_to FROM task WHERE assigned_to IS NOT NULL')
        tasks = cursor.fetchall()
        
        for task_id, assigned_to in tasks:
            cursor.execute('INSERT OR IGNORE INTO task_assignments (task_id, user_id) VALUES (?, ?)', 
                         (task_id, assigned_to))
        
        print(f"✓ {len(tasks)} görev assignment verisi aktarıldı")
        
        # assigned_to sütununu kaldır (SQLite'da doğrudan DROP COLUMN yok, tablo yeniden oluşturmak gerekiyor)
        # Önce yeni task tablosunu oluştur
        cursor.execute('''
            CREATE TABLE task_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(10) DEFAULT 'medium',
                due_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                created_by INTEGER NOT NULL,
                FOREIGN KEY (created_by) REFERENCES user (id)
            )
        ''')
        
        # Eski verilerini yeni tabloya kopyala (assigned_to hariç)
        cursor.execute('''
            INSERT INTO task_new (id, title, description, status, priority, due_date, 
                                created_at, updated_at, completed_at, created_by)
            SELECT id, title, description, status, priority, due_date, 
                   created_at, updated_at, completed_at, created_by
            FROM task
        ''')
        
        # Eski tabloyu sil ve yenisini yeniden adlandır
        cursor.execute('DROP TABLE task')
        cursor.execute('ALTER TABLE task_new RENAME TO task')
        
        print("✓ Task tablosu güncellendi (assigned_to sütunu kaldırıldı)")
        
        # İndeksleri yeniden oluştur
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_created_by ON task (created_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_status ON task (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_assignments_task ON task_assignments (task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_assignments_user ON task_assignments (user_id)')
        
        print("✓ İndeksler oluşturuldu")
        
        # Değişiklikleri kaydet
        conn.commit()
        print("✓ Tüm değişiklikler kaydedildi")
        
        # Kontrol et
        cursor.execute('SELECT COUNT(*) FROM task_assignments')
        assignment_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM task')
        task_count = cursor.fetchone()[0]
        
        print(f"✓ Migration tamamlandı: {task_count} görev, {assignment_count} atama")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Hata oluştu: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("Veritabanı Many-to-Many migration başlatılıyor...")
    migrate_database()
    print("Migration tamamlandı!")
