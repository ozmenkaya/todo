#!/bin/bash
# DigitalOcean PostgreSQL Direct Migration Script

echo "🔧 OneSignal Database Migration for DigitalOcean PostgreSQL"
echo "============================================="

# Database connection details (replace with your actual values)
# You can find these in DigitalOcean Dashboard > Databases > Your DB
DB_HOST="your-db-host.db.ondigitalocean.com"
DB_PORT="25060"
DB_NAME="defaultdb"
DB_USER="doadmin"
DB_PASSWORD="your-password"

echo "📡 Connecting to PostgreSQL database..."

# Create migration SQL file
cat > /tmp/onesignal_migration.sql << 'EOF'
-- OneSignal Database Migration
DO $$ 
BEGIN
    RAISE NOTICE 'Starting OneSignal column migration...';

    -- Add push_notifications_enabled
    BEGIN
        ALTER TABLE users ADD COLUMN push_notifications_enabled BOOLEAN DEFAULT true;
        RAISE NOTICE '✅ Added push_notifications_enabled column';
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE '⚠️  push_notifications_enabled column already exists';
    END;

    -- Add task_assignment_notifications  
    BEGIN
        ALTER TABLE users ADD COLUMN task_assignment_notifications BOOLEAN DEFAULT true;
        RAISE NOTICE '✅ Added task_assignment_notifications column';
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE '⚠️  task_assignment_notifications column already exists';
    END;

    -- Add task_completion_notifications
    BEGIN
        ALTER TABLE users ADD COLUMN task_completion_notifications BOOLEAN DEFAULT true;
        RAISE NOTICE '✅ Added task_completion_notifications column';
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE '⚠️  task_completion_notifications column already exists';
    END;

    -- Add reminder_notifications
    BEGIN
        ALTER TABLE users ADD COLUMN reminder_notifications BOOLEAN DEFAULT true;
        RAISE NOTICE '✅ Added reminder_notifications column';
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE '⚠️  reminder_notifications column already exists';
    END;

    -- Add report_notifications
    BEGIN
        ALTER TABLE users ADD COLUMN report_notifications BOOLEAN DEFAULT true;
        RAISE NOTICE '✅ Added report_notifications column';
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE '⚠️  report_notifications column already exists';
    END;

    -- Add onesignal_player_id
    BEGIN
        ALTER TABLE users ADD COLUMN onesignal_player_id VARCHAR(255);
        RAISE NOTICE '✅ Added onesignal_player_id column';
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE '⚠️  onesignal_player_id column already exists';
    END;

    RAISE NOTICE '🎉 OneSignal migration completed!';
END $$;
EOF

# Run the migration
echo "🚀 Running migration..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f /tmp/onesignal_migration.sql

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
    echo "📊 Verifying columns..."
    
    # Verify columns were added
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT column_name, data_type, is_nullable, column_default 
    FROM information_schema.columns 
    WHERE table_name = 'users' 
    AND column_name IN ('push_notifications_enabled', 'task_assignment_notifications', 'task_completion_notifications', 'reminder_notifications', 'report_notifications', 'onesignal_player_id')
    ORDER BY column_name;"
    
else
    echo "❌ Migration failed!"
    exit 1
fi

echo "🎯 You can now restart your application to use OneSignal notifications!"