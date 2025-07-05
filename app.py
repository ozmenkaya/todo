from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# Jinja2 filtre fonksiyonları
def nl2br(value):
    """Yeni satırları <br> etiketlerine çevirir"""
    return value.replace('\n', '<br>')

def moment_utcnow():
    """Şu anki UTC zamanını döndürür"""
    return datetime.utcnow()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo_company.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Jinja2 filtrelerini kaydet
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.globals['moment'] = type('obj', (object,), {'utcnow': moment_utcnow})

# Many-to-Many ilişki tablosu (görev atamaları için)
task_assignments = db.Table('task_assignments',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Veritabanı Modelleri
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='employee')  # 'admin', 'manager', 'employee'
    department = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    assigned_tasks = db.relationship('Task', secondary=task_assignments, back_populates='assignees', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', lazy='dynamic')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'cancelled'
    priority = db.Column(db.String(10), default='medium')  # 'low', 'medium', 'high', 'urgent'
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişkiler
    assignees = db.relationship('User', secondary=task_assignments, back_populates='assigned_tasks')
    creator = db.relationship('User', foreign_keys=[created_by], overlaps="created_tasks")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişkiler
    task = db.relationship('Task', backref='comments')
    user = db.relationship('User', backref='comments')

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reminder_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişki
    user = db.relationship('User', backref='reminders')

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
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
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

if __name__ == '__main__':
    import os
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    # Production için port'u environment variable'dan al
    port = int(os.environ.get('PORT', 5004))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
