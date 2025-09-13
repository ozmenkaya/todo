-- OneSignal Production Database Migration SQL
-- Run this directly on DigitalOcean PostgreSQL database if needed

-- Check if columns exist first
DO $$ 
BEGIN
    -- Add push_notifications_enabled column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='push_notifications_enabled') THEN
        ALTER TABLE users ADD COLUMN push_notifications_enabled BOOLEAN DEFAULT true;
    END IF;

    -- Add task_assignment_notifications column  
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='task_assignment_notifications') THEN
        ALTER TABLE users ADD COLUMN task_assignment_notifications BOOLEAN DEFAULT true;
    END IF;

    -- Add task_completion_notifications column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='task_completion_notifications') THEN
        ALTER TABLE users ADD COLUMN task_completion_notifications BOOLEAN DEFAULT true;
    END IF;

    -- Add reminder_notifications column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='reminder_notifications') THEN
        ALTER TABLE users ADD COLUMN reminder_notifications BOOLEAN DEFAULT true;
    END IF;

    -- Add report_notifications column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='report_notifications') THEN
        ALTER TABLE users ADD COLUMN report_notifications BOOLEAN DEFAULT true;
    END IF;

    -- Add onesignal_player_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='onesignal_player_id') THEN
        ALTER TABLE users ADD COLUMN onesignal_player_id VARCHAR(255);
    END IF;

END $$;

-- Verify columns were added
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('push_notifications_enabled', 'task_assignment_notifications', 'task_completion_notifications', 'reminder_notifications', 'report_notifications', 'onesignal_player_id')
ORDER BY column_name;