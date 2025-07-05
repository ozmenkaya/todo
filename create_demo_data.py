"""
Demo veri oluşturma scripti
Bu script ile sisteme örnek kullanıcılar ve görevler ekleyebilirsiniz.
"""

from app import app, db, User, Task, Reminder
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_demo_data():
    with app.app_context():
        # Demo kullanıcıları oluştur
        users_data = [
            {
                'username': 'manager1',
                'email': 'manager1@company.com',
                'password': 'manager123',
                'role': 'manager',
                'department': 'IT'
            },
            {
                'username': 'manager2',
                'email': 'manager2@company.com',
                'password': 'manager123',
                'role': 'manager',
                'department': 'Pazarlama'
            },
            {
                'username': 'employee1',
                'email': 'employee1@company.com',
                'password': 'employee123',
                'role': 'employee',
                'department': 'IT'
            },
            {
                'username': 'employee2',
                'email': 'employee2@company.com',
                'password': 'employee123',
                'role': 'employee',
                'department': 'IT'
            },
            {
                'username': 'employee3',
                'email': 'employee3@company.com',
                'password': 'employee123',
                'role': 'employee',
                'department': 'Pazarlama'
            }
        ]
        
        created_users = {}
        for user_data in users_data:
            # Kullanıcı zaten var mı kontrol et
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role'],
                    department=user_data['department']
                )
                db.session.add(user)
                db.session.flush()  # ID'yi al
                created_users[user_data['username']] = user
                print(f"✓ {user_data['username']} kullanıcısı oluşturuldu ({user_data['role']} - {user_data['department']})")
            else:
                created_users[user_data['username']] = existing_user
                print(f"- {user_data['username']} kullanıcısı zaten mevcut")
        
        # Admin kullanıcıyı da ekle
        admin = User.query.filter_by(username='admin').first()
        if admin:
            created_users['admin'] = admin
        
        # Demo görevleri oluştur (birden fazla atama da dahil)
        tasks_data = [
            {
                'title': 'Website Yenileme Projesi',
                'description': 'Şirket websitesinin modern tasarımla yenilenmesi ve mobil uyumlu hale getirilmesi',
                'assigned_to': ['employee1', 'employee2'],  # Birden fazla kişi
                'created_by': 'manager1',
                'priority': 'high',
                'status': 'in_progress'
            },
            {
                'title': 'Veritabanı Yedekleme Sistemi',
                'description': 'Otomatik veritabanı yedekleme sisteminin kurulması ve test edilmesi',
                'assigned_to': ['employee2'],
                'created_by': 'admin',
                'priority': 'urgent',
                'status': 'pending'
            },
            {
                'title': 'Sosyal Medya Kampanyası',
                'description': 'Yeni ürün lansmanı için sosyal medya kampanyasının hazırlanması',
                'assigned_to': ['employee3', 'manager2'],  # Manager ve employee birlikte
                'created_by': 'manager2',
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'title': 'Manager Eğitimi Organizasyonu',
                'description': 'Yeni manager eğitimi programının planlanması ve organizasyonu',
                'assigned_to': ['manager1', 'manager2'],  # İki manager birlikte
                'created_by': 'admin',
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'title': 'Güvenlik Denetimi',
                'description': 'IT altyapısının güvenlik denetimi ve rapor hazırlanması',
                'assigned_to': ['manager1'],
                'created_by': 'admin',
                'priority': 'high',
                'status': 'in_progress'
            },
            {
                'title': 'Müşteri Memnuniyet Anketi',
                'description': 'Q2 müşteri memnuniyet anketinin hazırlanması ve uygulanması',
                'assigned_to': ['employee3'],
                'created_by': 'manager2',
                'priority': 'low',
                'status': 'completed'
            },
            {
                'title': 'Departman Arası İşbirliği Projesi',
                'description': 'Tüm departmanların katılacağı büyük bir işbirliği projesi',
                'assigned_to': ['employee1', 'employee2', 'employee3', 'manager1'],  # Çok kişili atama
                'created_by': 'admin',
                'priority': 'high',
                'status': 'pending'
            }
        ]
        
        for task_data in tasks_data:
            # Görev zaten var mı kontrol et
            existing_task = Task.query.filter_by(title=task_data['title']).first()
            if not existing_task:
                creator_user = created_users.get(task_data['created_by'])
                
                if creator_user:
                    task = Task(
                        title=task_data['title'],
                        description=task_data['description'],
                        created_by=creator_user.id,
                        priority=task_data['priority'],
                        status=task_data['status'],
                        due_date=datetime.now() + timedelta(days=7) if task_data['priority'] == 'urgent' else datetime.now() + timedelta(days=14)
                    )
                    
                    # Atanacak kullanıcıları Many-to-Many ilişkiye ekle
                    assigned_users = []
                    for username in task_data['assigned_to']:
                        user = created_users.get(username)
                        if user:
                            task.assignees.append(user)
                            assigned_users.append(username)
                    
                    if task_data['status'] == 'completed':
                        task.completed_at = datetime.now() - timedelta(days=1)
                    
                    db.session.add(task)
                    assigned_str = ', '.join(assigned_users)
                    print(f"✓ '{task_data['title']}' görevi oluşturuldu ({task_data['created_by']} → {assigned_str})")
            else:
                print(f"- '{task_data['title']}' görevi zaten mevcut")
        
        # Demo anımsatıcıları oluştur
        reminders_data = [
            {
                'title': 'Haftalık Takım Toplantısı',
                'description': 'Her pazartesi 09:00\'da takım toplantısı',
                'user': 'manager1',
                'hours_from_now': 24
            },
            {
                'title': 'Proje Deadline Kontrolü',
                'description': 'Website projesi deadline yaklaşıyor',
                'user': 'manager1',
                'hours_from_now': 8
            },
            {
                'title': 'Müşteri Sunumu Hazırlığı',
                'description': 'Yarınki müşteri sunumu için son hazırlıklar',
                'user': 'employee3',
                'hours_from_now': 4
            }
        ]
        
        for reminder_data in reminders_data:
            user = created_users.get(reminder_data['user'])
            if user:
                existing_reminder = Reminder.query.filter_by(
                    title=reminder_data['title'],
                    user_id=user.id
                ).first()
                
                if not existing_reminder:
                    reminder = Reminder(
                        title=reminder_data['title'],
                        description=reminder_data['description'],
                        user_id=user.id,
                        reminder_date=datetime.now() + timedelta(hours=reminder_data['hours_from_now'])
                    )
                    db.session.add(reminder)
                    print(f"✓ '{reminder_data['title']}' anımsatıcısı oluşturuldu ({reminder_data['user']})")
                else:
                    print(f"- '{reminder_data['title']}' anımsatıcısı zaten mevcut")
        
        try:
            db.session.commit()
            print("\n🎉 Demo veriler başarıyla oluşturuldu!")
            print("\n👥 Demo Kullanıcılar:")
            print("   Admin: admin / admin123")
            print("   Manager (IT): manager1 / manager123")
            print("   Manager (Pazarlama): manager2 / manager123")
            print("   Employee (IT): employee1 / employee123")
            print("   Employee (IT): employee2 / employee123")
            print("   Employee (Pazarlama): employee3 / employee123")
            print("\n💡 Özellik Testleri:")
            print("   - manager1 ile giriş yapın ve 'Atadıklarım' sekmesini kontrol edin")
            print("   - employee1 ile giriş yapın ve hem atanan hem atadığı görevleri görün")
            print("   - Anımsatıcıları test etmek için farklı kullanıcılarla giriş yapın")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Hata oluştu: {e}")

if __name__ == '__main__':
    print("Demo veri oluşturuluyor...")
    create_demo_data()
