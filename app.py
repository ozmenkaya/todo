from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# Models import
from models import db, User, Task, Comment, Reminder, task_assignments

# Jinja2 filtre fonksiyonları
def nl2br(value):
    """Yeni satırları <br> etiketlerine çevirir"""
    return value.replace('\n', '<br>')

def moment_utcnow():
    """Şu anki UTC zamanını döndürür"""
    return datetime.utcnow()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Database configuration - PostgreSQL for production, SQLite for development
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # DigitalOcean PostgreSQL URL düzeltmesi
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Production PostgreSQL ayarları
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'max_overflow': 0,
        }
else:
    # SQLite fallback (development veya PostgreSQL henüz hazır değilse)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_company.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@helmex.com')

# Initialize extensions with app
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Jinja2 filtrelerini kaydet
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.globals['moment'] = type('obj', (object,), {'utcnow': moment_utcnow})

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ana sayfa
@app.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        # Admin tüm görevleri görebilir
        tasks = Task.query.filter(Task.status != 'completed').order_by(Task.created_at.desc()).all()
        completed_tasks = Task.query.filter_by(status='completed').order_by(Task.updated_at.desc()).all()
        assigned_tasks = current_user.assigned_tasks.filter(Task.status != 'completed').order_by(Task.created_at.desc()).all()
        assigned_completed_tasks = current_user.assigned_tasks.filter_by(status='completed').order_by(Task.updated_at.desc()).all()
        created_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status != 'completed').order_by(Task.created_at.desc()).all()
        created_completed_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status == 'completed').order_by(Task.updated_at.desc()).all()
    elif current_user.role == 'manager':
        # Manager kendi departmanındaki görevleri görebilir
        dept_users = User.query.filter_by(department=current_user.department).all()
        user_ids = [user.id for user in dept_users]
        # Departmandaki kullanıcılara atanan aktif görevleri bul
        tasks = Task.query.join(task_assignments).join(User).filter(User.id.in_(user_ids), Task.status != 'completed').order_by(Task.created_at.desc()).all()
        # Departmandaki tamamlanan görevler
        completed_tasks = Task.query.join(task_assignments).join(User).filter(User.id.in_(user_ids), Task.status == 'completed').order_by(Task.updated_at.desc()).all()
        # Manager'ın atadığı aktif görevler
        created_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status != 'completed').order_by(Task.created_at.desc()).all()
        created_completed_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status == 'completed').order_by(Task.updated_at.desc()).all()
        # Manager'a atanan aktif görevler
        assigned_tasks = current_user.assigned_tasks.filter(Task.status != 'completed').order_by(Task.created_at.desc()).all()
        assigned_completed_tasks = current_user.assigned_tasks.filter_by(status='completed').order_by(Task.updated_at.desc()).all()
    else:
        # Employee sadece kendine atanan görevleri görebilir
        assigned_tasks = current_user.assigned_tasks.filter(Task.status != 'completed').order_by(Task.created_at.desc()).all()
        assigned_completed_tasks = current_user.assigned_tasks.filter_by(status='completed').order_by(Task.updated_at.desc()).all()
        # Employee'nin oluşturduğu görevler (eğer varsa)
        created_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status != 'completed').order_by(Task.created_at.desc()).all()
        created_completed_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status == 'completed').order_by(Task.updated_at.desc()).all()
        tasks = assigned_tasks
        completed_tasks = assigned_completed_tasks
    
    return render_template('index.html', 
                         tasks=tasks, 
                         assigned_tasks=assigned_tasks, 
                         created_tasks=created_tasks,
                         completed_tasks=completed_tasks,
                         assigned_completed_tasks=assigned_completed_tasks if current_user.role != 'employee' else [],
                         created_completed_tasks=created_completed_tasks if current_user.role != 'employee' else [])

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"🔍 Login attempt - Username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"✅ User found: {user.username} | Role: {user.role}")
            print(f"🔐 Password check...")
            
            if check_password_hash(user.password_hash, password):
                print(f"✅ Password correct for user: {username}")
                login_user(user)
                print(f"✅ User logged in successfully: {username}")
                return redirect(url_for('index'))
            else:
                print(f"❌ Password incorrect for user: {username}")
                flash('Geçersiz kullanıcı adı veya şifre!')
        else:
            print(f"❌ User not found: {username}")
            flash('Geçersiz kullanıcı adı veya şifre!')
    
    return render_template('login.html')

# Çıkış
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Yeni görev oluşturma
@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if current_user.role == 'employee':
        flash('Görev oluşturma yetkiniz yok!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        assigned_to_list = request.form.getlist('assigned_to')  # Çoklu seçim için getlist kullan
        priority = request.form['priority']
        due_date_str = request.form['due_date']
        
        if not assigned_to_list:
            flash('En az bir kişi seçmelisiniz!')
            # Kullanıcı listesini yeniden yükle
            if current_user.role == 'admin':
                users = User.query.all()
            else:  # manager
                dept_users = User.query.filter_by(department=current_user.department).all()
                other_managers = User.query.filter_by(role='manager').all()
                user_ids = set()
                users = []
                for user in dept_users + other_managers:
                    if user.id not in user_ids:
                        users.append(user)
                        user_ids.add(user.id)
            return render_template('create_task.html', users=users)
        
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        
        # Yeni görev oluştur
        task = Task(
            title=title,
            description=description,
            created_by=current_user.id,
            priority=priority,
            due_date=due_date
        )
        
        # Atanacak kullanıcıları ekle
        assignees = User.query.filter(User.id.in_(assigned_to_list)).all()
        for assignee in assignees:
            task.assignees.append(assignee)
        
        db.session.add(task)
        db.session.commit()
        
        # Acil görevler için mail gönder
        if priority == 'urgent':
            try:
                send_urgent_task_email(task, assignees)
                flash(f'🚨 Acil görev oluşturuldu ve {len(assigned_to_list)} kişiye mail gönderildi!')
            except:
                flash(f'⚠️ Görev oluşturuldu ama mail gönderilemedi. {len(assigned_to_list)} kişiye atandı.')
        else:
            if len(assigned_to_list) == 1:
                flash('Görev başarıyla oluşturuldu!')
            else:
                flash(f'Görev başarıyla oluşturuldu ve {len(assigned_to_list)} kişiye atandı!')
        
        return redirect(url_for('index'))
    
    # Kullanıcı listesi - Manager'lar diğer manager ve çalışanlara atayabilir
    if current_user.role == 'admin':
        users = User.query.all()
    else:  # manager
        # Manager kendi departmanındaki herkesi + diğer manager'ları görebilir
        dept_users = User.query.filter_by(department=current_user.department).all()
        other_managers = User.query.filter_by(role='manager').all()
        # Çakışmaları önlemek için set kullan
        user_ids = set()
        users = []
        for user in dept_users + other_managers:
            if user.id not in user_ids:
                users.append(user)
                user_ids.add(user.id)
    
    return render_template('create_task.html', users=users)

# Görev detayı
@app.route('/task/<int:task_id>')
@login_required
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü - görev atanmışlardan birisi mi kontrol et
    if current_user.role == 'employee' and current_user not in task.assignees:
        flash('Bu görevi görme yetkiniz yok!')
        return redirect(url_for('index'))
    
    comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.desc()).all()
    return render_template('task_detail.html', task=task, comments=comments)

# Görev durumu güncelleme
@app.route('/update_task_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form['status']
    
    # Yetki kontrolü - görev atanmışlardan birisi mi kontrol et
    if current_user.role == 'employee' and current_user not in task.assignees:
        return jsonify({'error': 'Yetkiniz yok!'}), 403
    
    task.status = new_status
    task.updated_at = datetime.utcnow()
    
    if new_status == 'completed':
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
    flash('Görev durumu güncellendi!')
    return redirect(url_for('task_detail', task_id=task_id))

# Yorum ekleme
@app.route('/add_comment/<int:task_id>', methods=['POST'])
@login_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    content = request.form['content']
    
    comment = Comment(
        content=content,
        task_id=task_id,
        user_id=current_user.id
    )
    
    db.session.add(comment)
    db.session.commit()
    flash('Yorum eklendi!')
    return redirect(url_for('task_detail', task_id=task_id))

# Kullanıcı yönetimi (sadece admin)
@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!')
        return redirect(url_for('index'))
    
    users = User.query.all()
    
    # Her kullanıcı için istatistikleri hesapla
    for user in users:
        user.task_stats = {
            'assigned': user.assigned_tasks.count(),
            'created': user.created_tasks.count(),
            'completed': user.assigned_tasks.filter_by(status='completed').count(),
            'pending': user.assigned_tasks.filter_by(status='pending').count(),
            'in_progress': user.assigned_tasks.filter_by(status='in_progress').count(),
            'reminders': len(user.reminders),
            'comments': len(user.comments)
        }
    
    return render_template('users.html', users=users)

# Yeni kullanıcı ekleme
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Kullanıcı ekleme yetkiniz yok!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        department = request.form['department']
        
        # Kullanıcı zaten var mı kontrol et
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!')
            return render_template('add_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor!')
            return render_template('add_user.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            department=department
        )
        
        db.session.add(user)
        db.session.commit()
        flash('Kullanıcı başarıyla eklendi!')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')

# Kullanıcı silme
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Kullanıcı silme yetkiniz yok!')
        return redirect(url_for('users'))
    
    user = User.query.get_or_404(user_id)
    
    # Kendini silmeye çalışıyor mu?
    if user.id == current_user.id:
        flash('Kendi hesabınızı silemezsiniz!')
        return redirect(url_for('users'))
    
    # Kullanıcının görevlerini kontrol et
    assigned_tasks_count = user.assigned_tasks.count()
    created_tasks = Task.query.filter_by(created_by=user.id).count()
    user_reminders = Reminder.query.filter_by(user_id=user.id).count()
    user_comments = Comment.query.filter_by(user_id=user.id).count()
    
    try:
        # İlişkili verileri temizle
        if assigned_tasks_count > 0:
            # Kullanıcının atanmış olduğu görevlerden çıkar
            for task in user.assigned_tasks:
                task.assignees.remove(user)
                # Eğer görevde başka atanmış kişi yoksa, admin'i ata
                if not task.assignees:
                    task.assignees.append(current_user)
        
        if created_tasks > 0:
            # Oluşturduğu görevleri admin'e aktar
            Task.query.filter_by(created_by=user.id).update({'created_by': current_user.id})
        
        # Anımsatıcıları sil
        if user_reminders > 0:
            Reminder.query.filter_by(user_id=user.id).delete()
        
        # Yorumları admin'e aktar
        if user_comments > 0:
            Comment.query.filter_by(user_id=user.id).update({'user_id': current_user.id})
        
        # Kullanıcıyı sil
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Kullanıcı "{user.username}" başarıyla silindi! İlişkili veriler size aktarıldı.')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Kullanıcı silinirken hata oluştu: {str(e)}')
    
    return redirect(url_for('users'))

# Kullanıcı düzenleme
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Kullanıcı düzenleme yetkiniz yok!')
        return redirect(url_for('users'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        department = request.form['department']
        new_password = request.form.get('new_password', '').strip()
        
        # Kullanıcı adı ve e-posta kontrolü (kendi dışında)
        if User.query.filter(User.username == username, User.id != user.id).first():
            flash('Bu kullanıcı adı başka bir kullanıcı tarafından kullanılıyor!')
            # İstatistikleri hesapla
            user.task_stats = {
                'assigned': user.assigned_tasks.count(),
                'created': user.created_tasks.count(),
                'completed': user.assigned_tasks.filter_by(status='completed').count(),
                'pending': user.assigned_tasks.filter_by(status='pending').count(),
                'in_progress': user.assigned_tasks.filter_by(status='in_progress').count(),
                'reminders': len(user.reminders),
                'comments': len(user.comments)
            }
            return render_template('edit_user.html', user=user)
        
        if User.query.filter(User.email == email, User.id != user.id).first():
            flash('Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor!')
            # İstatistikleri hesapla
            user.task_stats = {
                'assigned': user.assigned_tasks.count(),
                'created': user.created_tasks.count(),
                'completed': user.assigned_tasks.filter_by(status='completed').count(),
                'pending': user.assigned_tasks.filter_by(status='pending').count(),
                'in_progress': user.assigned_tasks.filter_by(status='in_progress').count(),
                'reminders': len(user.reminders),
                'comments': len(user.comments)
            }
            return render_template('edit_user.html', user=user)
        
        # Kullanıcı bilgilerini güncelle
        user.username = username
        user.email = email
        user.role = role
        user.department = department
        
        # Şifre değiştirilecek mi?
        if new_password:
            if len(new_password) < 6:
                flash('Yeni şifre en az 6 karakter olmalıdır!')
                # İstatistikleri hesapla
                user.task_stats = {
                    'assigned': user.assigned_tasks.count(),
                    'created': user.created_tasks.count(),
                    'completed': user.assigned_tasks.filter_by(status='completed').count(),
                    'pending': user.assigned_tasks.filter_by(status='pending').count(),
                    'in_progress': user.assigned_tasks.filter_by(status='in_progress').count(),
                    'reminders': len(user.reminders),
                    'comments': len(user.comments)
                }
                return render_template('edit_user.html', user=user)
            user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash(f'Kullanıcı "{user.username}" başarıyla güncellendi!')
            return redirect(url_for('users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kullanıcı güncellenirken hata oluştu: {str(e)}')
    
    # İstatistikleri hesapla
    user.task_stats = {
        'assigned': user.assigned_tasks.count(),
        'created': user.created_tasks.count(),
        'completed': user.assigned_tasks.filter_by(status='completed').count(),
        'pending': user.assigned_tasks.filter_by(status='pending').count(),
        'in_progress': user.assigned_tasks.filter_by(status='in_progress').count(),
        'reminders': len(user.reminders),
        'comments': len(user.comments)
    }
    
    return render_template('edit_user.html', user=user)

# İstatistikler
@app.route('/stats')
@login_required
def stats():
    if current_user.role == 'employee':
        flash('İstatistikleri görme yetkiniz yok!')
        return redirect(url_for('index'))
    
    # Temel istatistikler
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status='completed').count()
    pending_tasks = Task.query.filter_by(status='pending').count()
    in_progress_tasks = Task.query.filter_by(status='in_progress').count()
    
    # Departman bazında istatistikler (admin için)
    dept_stats = []
    if current_user.role == 'admin':
        departments = db.session.query(User.department).distinct().all()
        for dept in departments:
            if dept[0]:  # None olmayan departmanlar
                dept_users = User.query.filter_by(department=dept[0]).all()
                user_ids = [user.id for user in dept_users]
                # Many-to-Many ilişki ile departman görevlerini say
                dept_total = Task.query.join(task_assignments).join(User).filter(User.id.in_(user_ids)).count()
                dept_completed = Task.query.join(task_assignments).join(User).filter(User.id.in_(user_ids), Task.status=='completed').count()
                dept_stats.append({
                    'department': dept[0],
                    'total': dept_total,
                    'completed': dept_completed,
                    'completion_rate': round((dept_completed/dept_total*100) if dept_total > 0 else 0, 1)
                })
    
    stats_data = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': round((completed_tasks/total_tasks*100) if total_tasks > 0 else 0, 1),
        'dept_stats': dept_stats
    }
    
    return render_template('stats.html', stats=stats_data)

# Anımsatıcılar
@app.route('/reminders')
@login_required
def reminders():
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.reminder_date.asc()).all()
    return render_template('reminders.html', reminders=reminders)

# Yeni anımsatıcı ekleme
@app.route('/add_reminder', methods=['GET', 'POST'])
@login_required
def add_reminder():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        reminder_date_str = request.form['reminder_date']
        reminder_time_str = request.form.get('reminder_time', '09:00')
        
        # Tarih ve saati birleştir
        reminder_datetime = datetime.strptime(f"{reminder_date_str} {reminder_time_str}", '%Y-%m-%d %H:%M')
        
        reminder = Reminder(
            title=title,
            description=description,
            reminder_date=reminder_datetime,
            user_id=current_user.id
        )
        
        db.session.add(reminder)
        db.session.commit()
        flash('Anımsatıcı başarıyla eklendi!')
        return redirect(url_for('reminders'))
    
    return render_template('add_reminder.html')

# Anımsatıcı tamamlama
@app.route('/complete_reminder/<int:reminder_id>', methods=['POST'])
@login_required
def complete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Sadece kendi anımsatıcısını tamamlayabilir
    if reminder.user_id != current_user.id:
        flash('Bu anımsatıcıyı tamamlama yetkiniz yok!')
        return redirect(url_for('reminders'))
    
    reminder.is_completed = not reminder.is_completed
    db.session.commit()
    
    status = 'tamamlandı' if reminder.is_completed else 'tamamlanmadı'
    flash(f'Anımsatıcı {status} olarak işaretlendi!')
    return redirect(url_for('reminders'))

# Anımsatıcı silme
@app.route('/delete_reminder/<int:reminder_id>', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Sadece kendi anımsatıcısını silebilir
    if reminder.user_id != current_user.id:
        flash('Bu anımsatıcıyı silme yetkiniz yok!')
        return redirect(url_for('reminders'))
    
    db.session.delete(reminder)
    db.session.commit()
    flash('Anımsatıcı silindi!')
    return redirect(url_for('reminders'))

# Bugünün anımsatıcılarını API olarak getir
@app.route('/api/today_reminders')
@login_required
def api_today_reminders():
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    reminders = Reminder.query.filter(
        Reminder.user_id == current_user.id,
        Reminder.reminder_date >= today,
        Reminder.reminder_date < tomorrow,
        Reminder.is_completed == False
    ).all()
    
    reminder_list = []
    for reminder in reminders:
        reminder_list.append({
            'id': reminder.id,
            'title': reminder.title,
            'description': reminder.description,
            'time': reminder.reminder_date.strftime('%H:%M')
        })
    
    return jsonify(reminder_list)

def create_admin_user():
    """İlk admin kullanıcıyı oluştur"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@company.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            department='IT'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin kullanıcı oluşturuldu: admin / admin123")

# Mail gönderme fonksiyonu
def send_urgent_task_email(task, assignees):
    """Acil görev oluşturulduğunda mail gönderir"""
    try:
        # Development ortamında mail konfigürasyonu yoksa simüle et
        if not app.config.get('MAIL_USERNAME'):
            print(f"🚨 ACİL GÖREV MAİLİ (SİMÜLE EDİLDİ):")
            print(f"Görev: {task.title}")
            print(f"Alıcılar: {[assignee.email or assignee.username for assignee in assignees]}")
            return True
        
        # Debug: Mail konfigürasyonunu kontrol et
        print(f"🔧 Mail Server: {app.config.get('MAIL_SERVER')}")
        print(f"🔧 Mail Username: {app.config.get('MAIL_USERNAME')}")
        
        mail_sent_count = 0    
        # Her atanan kullanıcıya ayrı mail gönder
        for assignee in assignees:
            if assignee.email:  # Email adresi varsa
                print(f"📧 Mail gönderiliyor: {assignee.email}")
                msg = Message(
                    subject=f'🚨 ACİL GÖREV: {task.title}',
                    recipients=[assignee.email],
                    html=f'''
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                            <h1>🚨 ACİL GÖREV ATANDI</h1>
                        </div>
                        <div style="padding: 20px; background-color: #f8f9fa;">
                            <h2>{task.title}</h2>
                            <p><strong>Açıklama:</strong></p>
                            <div style="background-color: white; padding: 15px; border-left: 4px solid #dc3545; margin: 10px 0;">
                                {task.description.replace(chr(10), '<br>') if task.description else 'Açıklama yok'}
                            </div>
                            <p><strong>Öncelik:</strong> <span style="color: #dc3545; font-weight: bold;">ACİL</span></p>
                            <p><strong>Atayan:</strong> {task.creator.username}</p>
                            {f'<p><strong>Son Tarih:</strong> {task.due_date.strftime("%d.%m.%Y")}</p>' if task.due_date else ''}
                            <p><strong>Oluşturulma Tarihi:</strong> {task.created_at.strftime("%d.%m.%Y %H:%M")}</p>
                        </div>
                        <div style="background-color: #e9ecef; padding: 15px; text-align: center;">
                            <p style="margin: 0; color: #6c757d;">Bu görev acil olarak işaretlenmiştir. Lütfen en kısa sürede inceleyiniz.</p>
                            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 12px;">Helmex Todo Yönetim Sistemi</p>
                        </div>
                    </div>
                    '''
                )
                try:
                    mail.send(msg)
                    mail_sent_count += 1
                    print(f"✅ Mail gönderildi: {assignee.email}")
                except Exception as mail_error:
                    print(f"❌ Mail gönderme hatası ({assignee.email}): {mail_error}")
            else:
                print(f"❌ Email adresi yok: {assignee.username}")
        
        print(f"📊 Toplam {mail_sent_count} mail gönderildi")
        return True
    except Exception as e:
        print(f"❌ Genel mail gönderme hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
        return False

# Yedekleme sistemi routes
@app.route('/admin/backups')
@login_required
def backup_management():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!')
        return redirect(url_for('index'))
    
    try:
        from backup_system import TodoBackupManager
        backup_manager = TodoBackupManager()
        stats = backup_manager.get_backup_stats()
        
        # Yedek dosya listesi
        backup_files = []
        backup_dir = 'backups'
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.startswith('todo_backup_') and file.endswith('.zip'):
                    file_path = os.path.join(backup_dir, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append({
                        'name': file,
                        'size': file_size,
                        'date': file_time
                    })
        
        # Tarihe göre sırala (en yeni önce)
        backup_files.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template('backup_management.html', stats=stats, backup_files=backup_files)
        
    except Exception as e:
        flash(f'Yedekleme bilgileri alınamadı: {e}')
        return redirect(url_for('index'))

@app.route('/admin/backup/create', methods=['POST'])
@login_required
def create_backup():
    if current_user.role != 'admin':
        flash('Bu işlemi yapma yetkiniz yok!')
        return redirect(url_for('index'))
    
    try:
        from backup_system import TodoBackupManager
        backup_manager = TodoBackupManager()
        
        if backup_manager.create_backup():
            flash('✅ Yedekleme başarıyla tamamlandı!')
        else:
            flash('❌ Yedekleme sırasında hata oluştu!')
            
    except Exception as e:
        flash(f'Yedekleme hatası: {e}')
    
    return redirect(url_for('backup_management'))

@app.route('/admin/backup/download/<filename>')
@login_required
def download_backup(filename):
    if current_user.role != 'admin':
        flash('Bu işlemi yapma yetkiniz yok!')
        return redirect(url_for('index'))
    
    backup_dir = 'backups'
    return send_from_directory(backup_dir, filename, as_attachment=True)

@app.route('/debug/mail')
@login_required
def debug_mail():
    """Mail konfigürasyonunu debug etmek için"""
    if not current_user.role == 'admin':
        flash('Bu sayfaya erişim yetkiniz yok.')
        return redirect(url_for('index'))
    
    debug_info = {
        'MAIL_SERVER': app.config.get('MAIL_SERVER'),
        'MAIL_PORT': app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': '***' if app.config.get('MAIL_PASSWORD') else None,
        'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER'),
        'Flask Mail Extension': 'Loaded' if 'mail' in globals() else 'Not Loaded'
    }
    
    return jsonify(debug_info)

@app.route('/debug/test-mail')
@login_required
def test_mail():
    """Test mail gönderim"""
    if not current_user.role == 'admin':
        flash('Bu sayfaya erişim yetkiniz yok.')
        return redirect(url_for('index'))
    
    try:
        if not app.config.get('MAIL_USERNAME'):
            return jsonify({'status': 'error', 'message': 'Mail konfigürasyonu eksik'})
        
        if not current_user.email:
            return jsonify({'status': 'error', 'message': 'Kullanıcınızın email adresi yok'})
        
        msg = Message(
            subject='🧪 Test Mail - Helmex Todo',
            recipients=[current_user.email],
            html='''
            <h2>Test Mail</h2>
            <p>Bu bir test mailidir. Mail sistemi çalışıyor! ✅</p>
            <p>Gönderim zamanı: ''' + datetime.now().strftime('%d.%m.%Y %H:%M') + '''</p>
            '''
        )
        mail.send(msg)
        return jsonify({'status': 'success', 'message': f'Test mail gönderildi: {current_user.email}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Mail gönderme hatası: {str(e)}'})

if __name__ == '__main__':
    import os
    import time
    import sys
    
    # Database bağlantısını retry ile dene
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Database bağlantısını test et
                from sqlalchemy import text
                result = db.session.execute(text('SELECT 1'))
                print(f"✅ Database bağlantısı başarılı (attempt {attempt + 1})")
                
                # Tabloları oluştur
                db.create_all()
                print("✅ Tablolar oluşturuldu/güncellendi")
                
                # Admin kullanıcı oluştur
                create_admin_user()
                print("✅ Admin kullanıcı kontrolü tamamlandı")
                
                break  # Başarılı, döngüden çık
                
        except Exception as e:
            print(f"❌ Database bağlantı hatası (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                print(f"⏳ {retry_delay} saniye bekleyip tekrar denenecek...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("💥 Maximum retry sayısına ulaşıldı. SQLite fallback kullanılacak.")
                # SQLite fallback
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_company.db'
                with app.app_context():
                    db.create_all()
                    create_admin_user()
                break
    
    # Production için port'u environment variable'dan al
    port = int(os.environ.get('PORT', 5004))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🚀 Flask app başlatılıyor - Port: {port}, Debug: {debug}")
    app.run(debug=debug, host='0.0.0.0', port=port)
