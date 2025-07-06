#!/usr/bin/env python3
"""
Mail test script - Production'da mail ayarlarını kontrol eder
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def check_mail_config():
    with app.app_context():
        print("🔧 Mail Konfigürasyonu:")
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_PASSWORD: {'SET' if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print()
        
        print("👥 Kullanıcı Email Durumu:")
        users = User.query.all()
        for user in users:
            email_status = user.email if user.email else "❌ EMAIL YOK"
            print(f"- {user.username} ({user.role}): {email_status}")

if __name__ == '__main__':
    check_mail_config()
