#!/usr/bin/env python3
"""
OneSignal Migration Flask CLI Command

Production ortamında şu şekilde çalıştırın:
python -c "from app import app, db; from flask import Flask; from sqlalchemy import text; import sys; 

app_context = app.app_context()
app_context.push()

try:
    # Check existing columns
    result = db.session.execute(text('''
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
    '''))
    existing = [row[0] for row in result.fetchall()]
    print(f'Existing columns: {len(existing)}/6: {existing}')
    
    if len(existing) == 6:
        print('All OneSignal columns already exist!')
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
                db.session.execute(text(query))
                db.session.commit()
                added.append(col_name)
                print(f'Added: {col_name}')
            except Exception as e:
                print(f'Error adding {col_name}: {e}')
                db.session.rollback()
    
    print(f'Migration complete! Added {len(added)} columns')
    
except Exception as e:
    print(f'Migration failed: {e}')
    sys.exit(1)
finally:
    app_context.pop()
"