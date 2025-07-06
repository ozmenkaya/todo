#!/usr/bin/env python3
"""
Admin kullanıcı debug ve fix script'i
"""

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

def debug_admin_user():
    """Admin kullanıcı durumunu kontrol et ve düzelt"""
    
    print("🔍 Admin kullanıcı debug başlıyor...")
    
    try:
        # App ve models import
        from models import db, User
        from app import app
        
        with app.app_context():
            print("✅ App context aktif")
            
            # Tüm kullanıcıları listele
            all_users = User.query.all()
            print(f"📊 Toplam kullanıcı sayısı: {len(all_users)}")
            
            for user in all_users:
                print(f"👤 Kullanıcı: {user.username} | Email: {user.email} | Role: {user.role}")
            
            # Admin kullanıcıyı kontrol et
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                print(f"✅ Admin kullanıcı bulundu:")
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Role: {admin.role}")
                print(f"   Department: {admin.department}")
                print(f"   Password hash: {admin.password_hash[:20]}...")
                
                # Şifre kontrolü
                test_password = 'admin123'
                if check_password_hash(admin.password_hash, test_password):
                    print(f"✅ Şifre '{test_password}' doğru!")
                else:
                    print(f"❌ Şifre '{test_password}' yanlış!")
                    
                    # Şifreyi yeniden set et
                    print("🔧 Şifre yeniden ayarlanıyor...")
                    admin.password_hash = generate_password_hash('admin123')
                    db.session.commit()
                    print("✅ Şifre yenilendi: admin123")
                    
            else:
                print("❌ Admin kullanıcı bulunamadı!")
                print("🔧 Admin kullanıcı oluşturuluyor...")
                
                admin = User(
                    username='admin',
                    email='admin@helmex.com.tr',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    department='IT'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin kullanıcı oluşturuldu!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   Email: admin@helmex.com.tr")
                
            # Test kullanıcısı da oluştur
            test_user = User.query.filter_by(username='test').first()
            if not test_user:
                print("🔧 Test kullanıcısı oluşturuluyor...")
                test_user = User(
                    username='test',
                    email='test@helmex.com.tr',
                    password_hash=generate_password_hash('test123'),
                    role='manager',
                    department='Test'
                )
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test kullanıcı oluşturuldu: test / test123")
            
            print("🎉 Admin kullanıcı debug tamamlandı!")
            return True
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    success = debug_admin_user()
    
    if success:
        print("\n✅ GİRİŞ BİLGİLERİ:")
        print("Username: admin")
        print("Password: admin123")
        print("Role: admin")
    else:
        print("\n❌ Debug başarısız!")
        sys.exit(1)
