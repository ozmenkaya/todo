#!/usr/bin/env python3
"""
OneSignal Production Migration (Single File)
Bu dosyayı production sunucusuna upload edip çalıştırın
"""

# Production ortamında çalıştırılacak tek komut:
MIGRATION_COMMAND = '''python3 -c "
import os
import sys
sys.path.append('.')

# Import Flask app
from app import app, db
from sqlalchemy import text

print('🚀 OneSignal Migration Starting...')

with app.app_context():
    try:
        # Check existing columns
        result = db.session.execute(text(\\\"\\\"\\\"
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
            AND column_name IN (
                'push_notifications_enabled',
                'task_assignment_notifications', 
                'task_completion_notifications',
                'reminder_notifications',
                'report_notifications',
                'onesignal_player_id'
            )
        \\\"\\\"\\\"))
        
        existing = [row[0] for row in result.fetchall()]
        print(f'📋 Existing OneSignal columns: {len(existing)}/6')
        for col in existing:
            print(f'   ✓ {col}')
        
        if len(existing) == 6:
            print('✅ All OneSignal columns already exist!')
            sys.exit(0)
        
        # Add missing columns
        migrations = [
            ('push_notifications_enabled', 'ALTER TABLE users ADD COLUMN push_notifications_enabled BOOLEAN DEFAULT true'),
            ('task_assignment_notifications', 'ALTER TABLE users ADD COLUMN task_assignment_notifications BOOLEAN DEFAULT true'),
            ('task_completion_notifications', 'ALTER TABLE users ADD COLUMN task_completion_notifications BOOLEAN DEFAULT true'),
            ('reminder_notifications', 'ALTER TABLE users ADD COLUMN reminder_notifications BOOLEAN DEFAULT true'),
            ('report_notifications', 'ALTER TABLE users ADD COLUMN report_notifications BOOLEAN DEFAULT true'),
            ('onesignal_player_id', 'ALTER TABLE users ADD COLUMN onesignal_player_id VARCHAR(255)')
        ]
        
        added = []
        for col_name, query in migrations:
            if col_name not in existing:
                try:
                    print(f'📝 Adding: {col_name}')
                    db.session.execute(text(query))
                    db.session.commit()
                    added.append(col_name)
                    print(f'✅ Added: {col_name}')
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f'⏭️  {col_name} already exists')
                    else:
                        print(f'❌ Error adding {col_name}: {e}')
                        db.session.rollback()
        
        print(f'🎉 Migration complete! Added {len(added)} new columns')
        print('📱 OneSignal notifications now ready!')
        
    except Exception as e:
        print(f'💥 Migration failed: {e}')
        sys.exit(1)
"'''

def print_instructions():
    """Migration talimatlarını yazdır"""
    print("🚀 OneSignal Production Migration Instructions")
    print("=" * 60)
    print()
    print("📋 DigitalOcean App Platform Console'da şu komutu çalıştırın:")
    print()
    print(MIGRATION_COMMAND)
    print()
    print("📍 Adımlar:")
    print("1. DigitalOcean Dashboard → Apps → Your App")
    print("2. Console tab'ına tıklayın")
    print("3. Yukarıdaki komutu kopyala-yapıştır")
    print("4. Enter tuşuna basın")
    print("5. Migration sonucunu bekleyin")
    print()
    print("✅ Başarı durumunda: '🎉 Migration complete!' mesajı")
    print("❌ Hata durumunda: '💥 Migration failed:' + hata mesajı")
    print()

if __name__ == "__main__":
    print_instructions()