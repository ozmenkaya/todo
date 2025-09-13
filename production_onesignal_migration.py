#!/usr/bin/env python3
"""
Production OneSignal Database Migration Script

Bu script production PostgreSQL database'inde OneSignal notification 
sütunlarını ekler. DigitalOcean production ortamında çalıştırılmak üzere tasarlanmıştır.

Kullanım:
python production_onesignal_migration.py

Environment Variables:
- DATABASE_URL: PostgreSQL connection string (DigitalOcean tarafından sağlanan)
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_connection():
    """DigitalOcean DATABASE_URL'den PostgreSQL bağlantısı oluştur"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not found!")
        print("Bu script DigitalOcean production ortamında çalıştırılmalıdır.")
        return None
    
    try:
        # URL'yi parse et
        parsed = urlparse(database_url)
        
        # PostgreSQL bağlantı parametreleri
        conn_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:] if parsed.path else 'postgres',  # Remove leading /
            'user': parsed.username,
            'password': parsed.password,
            'sslmode': 'require'  # DigitalOcean managed DB requires SSL
        }
        
        print(f"🔗 Connecting to PostgreSQL...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        
        connection = psycopg2.connect(**conn_params)
        print("✅ Database connection successful!")
        return connection
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_columns_exist(cursor):
    """OneSignal sütunlarının zaten var olup olmadığını kontrol et"""
    try:
        # users tablosundaki sütunları listele
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
            AND column_name IN ('push_notifications_enabled', 'task_assignment_notifications', 
                               'task_completion_notifications', 'reminder_notifications', 
                               'report_notifications', 'onesignal_player_id')
            ORDER BY column_name;
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        return existing_columns
        
    except Exception as e:
        print(f"❌ Column check failed: {e}")
        return []

def migrate_onesignal_columns(connection):
    """OneSignal sütunlarını users tablosuna ekle"""
    cursor = connection.cursor()
    
    try:
        # Mevcut sütunları kontrol et
        existing_columns = check_columns_exist(cursor)
        
        if len(existing_columns) == 6:
            print("✅ All OneSignal columns already exist in database!")
            print(f"   Existing columns: {', '.join(existing_columns)}")
            return True
        elif existing_columns:
            print(f"⚠️  Some columns already exist: {', '.join(existing_columns)}")
        
        # Eklenecek sütunlar
        migration_queries = [
            ("push_notifications_enabled", "ALTER TABLE users ADD COLUMN push_notifications_enabled BOOLEAN DEFAULT true"),
            ("task_assignment_notifications", "ALTER TABLE users ADD COLUMN task_assignment_notifications BOOLEAN DEFAULT true"),
            ("task_completion_notifications", "ALTER TABLE users ADD COLUMN task_completion_notifications BOOLEAN DEFAULT true"),
            ("reminder_notifications", "ALTER TABLE users ADD COLUMN reminder_notifications BOOLEAN DEFAULT true"),
            ("report_notifications", "ALTER TABLE users ADD COLUMN report_notifications BOOLEAN DEFAULT true"),
            ("onesignal_player_id", "ALTER TABLE users ADD COLUMN onesignal_player_id VARCHAR(255)")
        ]
        
        # Her sütunu tek tek ekle
        added_columns = []
        skipped_columns = []
        
        for column_name, query in migration_queries:
            if column_name in existing_columns:
                print(f"⏭️  Skipping {column_name} (already exists)")
                skipped_columns.append(column_name)
                continue
                
            try:
                print(f"📝 Adding column: {column_name}")
                cursor.execute(query)
                connection.commit()
                added_columns.append(column_name)
                print(f"✅ Successfully added: {column_name}")
                
            except psycopg2.errors.DuplicateColumn:
                print(f"⏭️  Column {column_name} already exists (duplicate column error)")
                skipped_columns.append(column_name)
                connection.rollback()
                
            except Exception as e:
                print(f"❌ Failed to add column {column_name}: {e}")
                connection.rollback()
                return False
        
        # Sonuç raporu
        print("\n" + "="*50)
        print("🎯 MIGRATION SUMMARY:")
        print("="*50)
        
        if added_columns:
            print(f"✅ Added columns ({len(added_columns)}):")
            for col in added_columns:
                print(f"   - {col}")
        
        if skipped_columns:
            print(f"⏭️  Skipped columns ({len(skipped_columns)}):")
            for col in skipped_columns:
                print(f"   - {col}")
        
        # Verification
        print("\n🔍 Verifying migration...")
        final_columns = check_columns_exist(cursor)
        
        if len(final_columns) == 6:
            print("✅ ALL ONESIGNAL COLUMNS SUCCESSFULLY CREATED!")
            print("📱 Push notifications are now ready to work in production!")
            return True
        else:
            print(f"⚠️  Migration incomplete. Found {len(final_columns)}/6 columns")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main migration function"""
    print("🚀 OneSignal Production Database Migration")
    print("="*50)
    
    # Database bağlantısı kur
    connection = get_database_connection()
    
    if not connection:
        print("❌ Cannot connect to database. Exiting.")
        sys.exit(1)
    
    try:
        # Migration'ı çalıştır
        success = migrate_onesignal_columns(connection)
        
        if success:
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("🔄 Please restart your application to load the new schema.")
            sys.exit(0)
        else:
            print("\n💥 MIGRATION FAILED!")
            print("Check the error messages above for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    finally:
        connection.close()
        print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    main()