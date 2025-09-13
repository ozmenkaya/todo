from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import pytz
import gc
import weakref
from functools import lru_cache
import json
import requests

# Models import
from models import db, User, Task, Comment, Reminder, Report, ReportComment, task_assignments, report_shares, report_reads
from sqlalchemy import case

# Mail konfigürasyonu için kalıcı saklama
from mail_config import save_mail_config, load_mail_config, apply_mail_config_to_app

# Task priority sorting helper
def get_priority_order_clause():
    """
    Priority sıralaması için SQLAlchemy case ifadesi döndürür:
    1. urgent = 1 (en üst)
    2. high = 2
    3. medium = 3  
    4. low = 4 (en alt)
    """
    return case(
        (Task.priority == 'urgent', 1),
        (Task.priority == 'high', 2),
        (Task.priority == 'medium', 3),
        (Task.priority == 'low', 4),
        else_=5  # Belirsiz priority'ler en alta
    )

def apply_priority_date_sorting(query, date_column=None):
    """
    Task query'sine priority ve tarih sıralaması uygular:
    - Priority: urgent -> high -> medium -> low
    - Aynı priority içinde: En yeni tarih üstte (desc)
    """
    if date_column is None:
        date_column = Task.created_at
    
    return query.order_by(
        get_priority_order_clause().asc(),  # Priority: urgent=1 en üstte
        date_column.desc()  # Aynı priority içinde en yeni üstte
    )

# Timezone ayarları import
from timezone_config import (
    load_timezone_config, save_timezone_config, get_popular_timezones, 
    get_all_timezones, validate_timezone, get_current_timezone
)

# İstanbul timezone - dinamik olarak yüklenecek
def get_current_timezone_obj():
    """Mevcut timezone objesini döndürür"""
    config = load_timezone_config()
    return pytz.timezone(config['timezone'])

# Jinja2 filtre fonksiyonları
def nl2br(value):
    """Yeni satırları <br> etiketlerine çevirir"""
    return value.replace('\n', '<br>')

def moment_utcnow():
    """Şu anki UTC zamanını döndürür"""
    return datetime.utcnow()

def get_istanbul_time():
    """Mevcut timezone'da saati döndürür"""
    current_tz = get_current_timezone_obj()
    return datetime.now(current_tz)

def utc_to_istanbul(utc_dt):
    """UTC zamanını mevcut timezone'a çevirir"""
    if utc_dt is None:
        return None
    current_tz = get_current_timezone_obj()
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(current_tz)

def istanbul_to_utc(istanbul_dt):
    """Mevcut timezone'ı UTC'ye çevirir"""
    if istanbul_dt is None:
        return None
    if isinstance(istanbul_dt, str):
        istanbul_dt = datetime.strptime(istanbul_dt, '%Y-%m-%d %H:%M:%S')
    current_tz = get_current_timezone_obj()
    if istanbul_dt.tzinfo is None:
        istanbul_dt = current_tz.localize(istanbul_dt)
    return istanbul_dt.astimezone(pytz.utc).replace(tzinfo=None)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Expose OneSignal config to all templates
@app.context_processor
def inject_onesignal_config():
    return {
        'ONESIGNAL_APP_ID': os.environ.get('ONESIGNAL_APP_ID', ''),
        'ONESIGNAL_ALLOW_LOCALHOST': os.environ.get('ONESIGNAL_ALLOW_LOCALHOST', 'false')
    }

# Database configuration - PostgreSQL for production, SQLite for development
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # DigitalOcean PostgreSQL URL düzeltmesi
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Production PostgreSQL ayarları - RAM optimizasyonu
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 180,  # 3 dakika (300'den 180'e düştü)
            'pool_timeout': 10,   # 20'den 10'a düştü
            'max_overflow': 0,    # Overflow yok
            'pool_size': 3,       # Maximum 3 connection (default 5'ten düştü)
        }
else:
    # SQLite fallback (development veya PostgreSQL henüz hazır değilse)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_company.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'info@helmex.com.tr'  # Fallback
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or '4866Pars'  # Geçici - app password ile değiştir
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@helmex.com')

# Debug: Mail config'i log'la
print(f"🔧 Mail config - Username: {app.config['MAIL_USERNAME'][:4]}***")
print(f"🔧 Mail config - Password: {'SET' if app.config['MAIL_PASSWORD'] else 'NOT SET'}")

# Kaydedilmiş mail ayarlarını yükle
saved_mail_config = load_mail_config()
apply_mail_config_to_app(app, saved_mail_config)

# Flask-Mail başlatma
# Initialize extensions with app
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Remember cookie ayarları (30 gün)
from datetime import timedelta
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['REMEMBER_COOKIE_SECURE'] = False  # Development için False, production'da True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# Timezone-aware date formatting functions
def format_date_time(dt):
    """DateTime'ı timezone'a göre full format'ta döndürür"""
    if dt is None:
        return '-'
    config = load_timezone_config()
    converted_dt = utc_to_istanbul(dt)
    return converted_dt.strftime(config['display_format'])

def format_date_only(dt):
    """DateTime'ı timezone'a göre sadece tarih format'ta döndürür"""
    if dt is None:
        return '-'
    config = load_timezone_config()
    converted_dt = utc_to_istanbul(dt)
    return converted_dt.strftime(config['date_format'])

def format_time_only(dt):
    """DateTime'ı timezone'a göre sadece saat format'ta döndürür"""
    if dt is None:
        return '-'
    config = load_timezone_config()
    converted_dt = utc_to_istanbul(dt)
    return converted_dt.strftime(config['time_format'])

# Jinja2 filtrelerini kaydet
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['istanbul_time'] = utc_to_istanbul
app.jinja_env.filters['format_datetime'] = format_date_time
app.jinja_env.filters['format_date'] = format_date_only
app.jinja_env.filters['format_time'] = format_time_only

# Memory management ve cleanup handlers
@app.after_request
def after_request_cleanup(response):
    """Her request sonrası memory cleanup"""
    try:
        # Database session'ları temizle
        db.session.remove()
        
        # Garbage collection'ı tetikle (her 10 request'te bir)
        if hasattr(after_request_cleanup, 'counter'):
            after_request_cleanup.counter += 1
        else:
            after_request_cleanup.counter = 1
            
        if after_request_cleanup.counter % 10 == 0:
            gc.collect()
            after_request_cleanup.counter = 0
            
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Application context bitiminde session cleanup"""
    try:
        db.session.remove()
    except Exception as e:
        print(f"⚠️ Session cleanup error: {e}")

# Cache for frequently accessed data
@lru_cache(maxsize=32)
def get_user_by_id_cached(user_id):
    """User'ı cache ile getir"""
    return User.query.get(user_id)

@lru_cache(maxsize=16)  
def get_department_users_cached(department):
    """Department user'larını cache ile getir"""
    return User.query.filter_by(department=department).all()
app.jinja_env.globals['get_istanbul_time'] = get_istanbul_time
app.jinja_env.globals['get_timezone_config'] = load_timezone_config
app.jinja_env.globals['moment'] = type('obj', (object,), {
    'utcnow': moment_utcnow,
    'istanbul_now': get_istanbul_time
})

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ana sayfa
@app.route('/')
@login_required
def index():
    # Memory optimization: Limit queries to reduce RAM usage
    TASK_LIMIT = 50  # Her kategori için maksimum 50 görev
    
    if current_user.role == 'admin':
        # Admin tüm görevleri görebilir - priority ve tarih sıralaması ile
        tasks = apply_priority_date_sorting(
            Task.query.filter(Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        completed_tasks = Task.query.filter_by(status='completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
        assigned_tasks = apply_priority_date_sorting(
            current_user.assigned_tasks.filter(Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        assigned_completed_tasks = current_user.assigned_tasks.filter_by(status='completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
        created_tasks = apply_priority_date_sorting(
            Task.query.filter(Task.created_by == current_user.id, Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        created_completed_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status == 'completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
    elif current_user.role == 'manager':
        # Manager kendi departmanındaki görevleri görebilir - priority ve tarih sıralaması ile
        dept_users = get_department_users_cached(current_user.department)
        user_ids = [user.id for user in dept_users]
        # Departmandaki kullanıcılara atanan aktif görevleri bul - priority sıralaması
        tasks = apply_priority_date_sorting(
            Task.query.join(task_assignments).join(User).filter(User.id.in_(user_ids), Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        # Departmandaki tamamlanan görevler
        completed_tasks = Task.query.join(task_assignments).join(User).filter(User.id.in_(user_ids), Task.status == 'completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
        # Manager'ın atadığı aktif görevler - priority sıralaması
        created_tasks = apply_priority_date_sorting(
            Task.query.filter(Task.created_by == current_user.id, Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        created_completed_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status == 'completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
        # Manager'a atanan aktif görevler - priority sıralaması
        assigned_tasks = apply_priority_date_sorting(
            current_user.assigned_tasks.filter(Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        assigned_completed_tasks = current_user.assigned_tasks.filter_by(status='completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
    else:
        # Employee sadece kendine atanan görevleri görebilir - priority ve tarih sıralaması ile
        assigned_tasks = apply_priority_date_sorting(
            current_user.assigned_tasks.filter(Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        assigned_completed_tasks = current_user.assigned_tasks.filter_by(status='completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
        # Employee'nin oluşturduğu görevler - priority sıralaması
        created_tasks = apply_priority_date_sorting(
            Task.query.filter(Task.created_by == current_user.id, Task.status != 'completed')
        ).limit(TASK_LIMIT).all()
        created_completed_tasks = Task.query.filter(Task.created_by == current_user.id, Task.status == 'completed').order_by(Task.updated_at.desc()).limit(TASK_LIMIT).all()
        tasks = assigned_tasks
        completed_tasks = assigned_completed_tasks
    
    return render_template('index.html', 
                         tasks=tasks, 
                         assigned_tasks=assigned_tasks, 
                         created_tasks=created_tasks,
                         completed_tasks=completed_tasks,
                         assigned_completed_tasks=assigned_completed_tasks if current_user.role != 'employee' else [],
                         created_completed_tasks=created_completed_tasks if current_user.role != 'employee' else [])

# PWA Routes
@app.route('/manifest.json')
def manifest():
    """PWA Manifest dosyasını serve et"""
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def service_worker():
    """Service Worker dosyasını serve et"""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

# OneSignal SDK worker dosyalarını kökten serve et (OneSignal gereksinimi)
@app.route('/OneSignalSDKWorker.js')
def onesignal_sdk_worker():
    return send_from_directory('static', 'OneSignalSDKWorker.js', mimetype='application/javascript')

@app.route('/OneSignalSDKUpdaterWorker.js')
def onesignal_sdk_updater_worker():
    return send_from_directory('static', 'OneSignalSDKUpdaterWorker.js', mimetype='application/javascript')

@app.route('/api/current-time')
def current_time():
    """Mevcut timezone'da saati JSON olarak döndür"""
    try:
        current_time = get_istanbul_time()
        config = load_timezone_config()
        formatted_time = current_time.strftime(config['display_format'])
        return jsonify({
            'time': formatted_time,
            'timezone': config['timezone'],
            'timestamp': current_time.timestamp()
        })
    except Exception as e:
        print(f"Time API error: {e}")
        return jsonify({'error': 'Time unavailable'}), 500

@app.route('/offline')
def offline():
    """Çevrimdışı sayfası"""
    return render_template('offline.html')

@app.route('/api/app-info')
def app_info():
    """PWA uygulama bilgilerini döndür"""
    return jsonify({
        'name': 'Helmex Görev Yönetimi',
        'version': '1.0.0',
        'description': 'Şirket içi görev yönetim sistemi',
        'features': [
            'Görev oluşturma ve takip',
            'Hatırlatmalar',
            'Rapor paylaşımı',
            'Çevrimdışı çalışma',
            'Mobil uyumlu tasarım'
        ]
    })

# ---------------- OneSignal backend helper ----------------
def send_onesignal_notification(headings: dict, contents: dict, filters: list | None = None, include_aliases: dict | None = None):
    app_id = os.environ.get('ONESIGNAL_APP_ID')
    rest_api_key = os.environ.get('ONESIGNAL_REST_API_KEY')
    if not app_id or not rest_api_key:
        return False, 'OneSignal config missing'

    payload = {
        'app_id': app_id,
        'headings': headings,
        'contents': contents
    }
    if filters:
        payload['filters'] = filters
    if include_aliases:
        payload['include_aliases'] = include_aliases

    try:
        resp = requests.post(
            'https://api.onesignal.com/notifications',
            headers={
                'Authorization': f'Basic {rest_api_key}',
                'Content-Type': 'application/json'
            },
            data=json.dumps(payload),
            timeout=10
        )
        ok = 200 <= resp.status_code < 300
        return ok, (resp.json() if ok else resp.text)
    except Exception as e:
        return False, str(e)

@app.route('/admin/test_push', methods=['POST'])
@login_required
def admin_test_push():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    # Frontend, kullanıcıya "username" tag'i ekliyor; bu nedenle tag filtreleri ile hedefleyelim
    filters = [{
        "field": "tag",
        "key": "username",
        "relation": "=",
        "value": current_user.username
    }]
    ok, data = send_onesignal_notification(
        headings={"en": "Helmex"},
        contents={"en": "Test notification"},
        filters=filters
    )
    return jsonify({'ok': ok, 'data': data}), (200 if ok else 500)

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form  # "Beni hatırla" checkbox kontrolü
        
        print(f"🔍 Login attempt - Username: {username}")
        print(f"🔐 Remember me: {remember}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"✅ User found: {user.username} | Role: {user.role}")
            print(f"🔐 Password check...")
            
            if check_password_hash(user.password_hash, password):
                print(f"✅ Password correct for user: {username}")
                login_user(user, remember=remember)
                print(f"✅ User logged in successfully: {username} | Remember: {remember}")
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

# Gizlilik Politikası
@app.route('/privacy')
def privacy():
    """Gizlilik politikası sayfası"""
    return render_template('privacy.html')

# İletişim
@app.route('/contact')
def contact():
    """İletişim sayfası"""
    return render_template('contact.html')

# Kayıt Ol
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt sayfası"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        department = request.form['department'].strip()
        
        # Validation
        if not username or not email or not password or not department:
            flash('Tüm alanlar zorunludur!')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Şifreler eşleşmiyor!')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır!')
            return render_template('register.html')
        
        # Kullanıcı var mı kontrol et
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor!')
            return render_template('register.html')
        
        try:
            # Yeni kullanıcı oluştur (varsayılan olarak employee)
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role='employee',
                department=department,
                created_at=datetime.utcnow()
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hesap oluşturulurken hata oluştu: {str(e)}')
            return render_template('register.html')
    
    return render_template('register.html')

# Hesap Silme
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Kullanıcının kendi hesabını silmesi"""
    try:
        user_id = current_user.id
        username = current_user.username
        
        # Admin hesabı silinemez
        if current_user.role == 'admin':
            flash('Admin hesabı silinemez!')
            return redirect(url_for('index'))
        
        # Kullanıcının görevlerini kontrol et
        user_tasks = Task.query.filter(
            (Task.created_by == user_id) | 
            (Task.assignees.any(id=user_id))
        ).all()
        
        if user_tasks:
            flash('Hesabınızı silmeden önce tüm görevlerinizi tamamlamanız veya başka birine devretmeniz gerekiyor!')
            return redirect(url_for('index'))
        
        # Kullanıcıyı sil
        db.session.delete(current_user)
        db.session.commit()
        
        # Oturumu kapat
        logout_user()
        
        flash(f'{username} hesabı başarıyla silindi!')
        return redirect(url_for('login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Hesap silinirken hata oluştu: {str(e)}')
        return redirect(url_for('index'))

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
            try:
                # Kullanıcıdan gelen tarih İstanbul saati olarak kabul edilir
                istanbul_dt = datetime.strptime(due_date_str, '%Y-%m-%d')
                print(f"🕐 Due date input: {due_date_str} -> {istanbul_dt}")
                
                # İstanbul saatini UTC'ye çevir
                due_date = istanbul_to_utc(istanbul_dt)
                print(f"🕐 Due date UTC: {due_date}")
                
            except Exception as e:
                print(f"❌ Date conversion error: {e}")
                flash(f'Tarih formatı hatası: {str(e)}')
                return redirect(url_for('create_task'))
        
        # Yeni görev oluştur
        try:
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
            
            print(f"✅ Task created successfully: {task.title}")
            
            # Acil görevler için mail gönder
            if priority == 'urgent':
                try:
                    send_urgent_task_email(task, assignees)
                    flash(f'🚨 Acil görev oluşturuldu ve {len(assigned_to_list)} kişiye mail gönderildi!')
                except Exception as mail_error:
                    print(f"⚠️ Mail sending error: {mail_error}")
                    flash(f'⚠️ Görev oluşturuldu ama mail gönderilemedi. {len(assigned_to_list)} kişiye atandı.')
            else:
                if len(assigned_to_list) == 1:
                    flash('Görev başarıyla oluşturuldu!')
                else:
                    flash(f'Görev başarıyla oluşturuldu ve {len(assigned_to_list)} kişiye atandı!')
            
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"❌ Task creation error: {e}")
            db.session.rollback()
            flash(f'Görev oluşturma hatası: {str(e)}')
            return redirect(url_for('create_task'))
    
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
    
    # Görevi okundu olarak işaretle
    task.mark_as_read(current_user)
    
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
            'time': format_time_only(reminder.reminder_date)
        })
    
    return jsonify(reminder_list)

@app.route('/api/current-time')
def api_current_time():
    """Mevcut saati JSON olarak döndürür"""
    config = load_timezone_config()
    current_tz = pytz.timezone(config['timezone'])
    current_time = datetime.now(current_tz)
    
    return jsonify({
        'time': current_time.strftime(config['display_format']),
        'timezone': config['timezone'],
        'timestamp': current_time.isoformat()
    })

@app.route('/api/timezone-preview')
def api_timezone_preview():
    """Seçilen timezone'ın önizlemesini döndürür"""
    timezone_str = request.args.get('tz', 'Europe/Istanbul')
    
    try:
        if validate_timezone(timezone_str):
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz)
            
            # Varsayılan format kullan
            config = load_timezone_config()
            time_str = current_time.strftime(config['display_format'])
            
            return jsonify({
                'time': time_str,
                'timezone': timezone_str,
                'timestamp': current_time.isoformat()
            })
        else:
            return jsonify({'error': 'Invalid timezone'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                            {f'<p><strong>Son Tarih:</strong> {format_date_only(task.due_date)}</p>' if task.due_date else ''}
                            <p><strong>Oluşturulma Tarihi:</strong> {format_date_time(task.created_at)}</p>
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

@app.route('/admin/mail-settings', methods=['GET', 'POST'])
@login_required
def mail_settings():
    """Mail ayarları sayfası"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Form verilerini al
        mail_server = request.form.get('mail_server', '').strip()
        mail_port = request.form.get('mail_port', '').strip()
        mail_use_tls = request.form.get('mail_use_tls') == 'on'
        mail_username = request.form.get('mail_username', '').strip()
        mail_password = request.form.get('mail_password', '').strip()
        # Eğer şifre alanı boş veya sadece yıldız karakterleri ise mevcut şifreyi koru
        if not mail_password or mail_password.startswith('••••'):
            mail_password = app.config.get('MAIL_PASSWORD', '')
            print(f"🔧 Mevcut şifre korunuyor")
        mail_default_sender = request.form.get('mail_default_sender', '').strip()
        
        # Debug: Form verilerini log'la
        print(f"🔧 Form verileri alındı:")
        print(f"   Server: {mail_server}")
        print(f"   Port: {mail_port}")
        print(f"   TLS: {mail_use_tls}")
        print(f"   Username: {mail_username}")
        print(f"   Password: {'SET' if mail_password else 'EMPTY'}")
        print(f"   Sender: {mail_default_sender}")
        
        # Validasyon
        error_messages = []
        if not mail_server:
            error_messages.append('Mail server adresi gerekli')
        if not mail_port or not mail_port.isdigit():
            error_messages.append('Geçerli bir port numarası gerekli')
        if not mail_username:
            error_messages.append('Kullanıcı adı gerekli')
        if not mail_default_sender:
            error_messages.append('Gönderen adresi gerekli')
        
        if error_messages:
            for error_msg in error_messages:
                flash(error_msg, 'danger')
            return render_template('mail_settings.html', config=app.config)
        
        try:
            # Flask app config'i güncelle
            app.config['MAIL_SERVER'] = mail_server
            app.config['MAIL_PORT'] = int(mail_port)
            app.config['MAIL_USE_TLS'] = mail_use_tls
            app.config['MAIL_USERNAME'] = mail_username
            app.config['MAIL_PASSWORD'] = mail_password
            app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender
            
            # Mail ayarlarını dosyaya kaydet
            config_to_save = {
                'MAIL_SERVER': mail_server,
                'MAIL_PORT': int(mail_port),
                'MAIL_USE_TLS': mail_use_tls,
                'MAIL_USERNAME': mail_username,
                'MAIL_PASSWORD': mail_password,
                'MAIL_DEFAULT_SENDER': mail_default_sender
            }
            save_mail_config(config_to_save)
            
            # Mail extension'ı yeniden başlat
            global mail
            mail.init_app(app)
            
            flash('✅ Mail ayarları başarıyla güncellendi!', 'success')
            print(f"🔧 Mail ayarları güncellendi - Server: {mail_server}, Username: {mail_username[:4]}***")
            
        except Exception as e:
            flash(f'❌ Mail ayarları güncellenirken hata oluştu: {str(e)}', 'danger')
            print(f"❌ Mail ayarları güncelleme hatası: {e}")
    
    return render_template('mail_settings.html', config=app.config)

@app.route('/admin/timezone-settings', methods=['GET', 'POST'])
@login_required
def timezone_settings():
    """Timezone ayarları sayfası"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            timezone = request.form.get('timezone')
            display_format = request.form.get('display_format', '%d.%m.%Y %H:%M')
            date_format = request.form.get('date_format', '%d.%m.%Y')
            time_format = request.form.get('time_format', '%H:%M')
            
            # Timezone validation
            if not validate_timezone(timezone):
                flash('❌ Geçersiz timezone seçimi!', 'danger')
                return redirect(url_for('timezone_settings'))
            
            # Yeni ayarları kaydet
            new_config = {
                'timezone': timezone,
                'display_format': display_format,
                'date_format': date_format,
                'time_format': time_format
            }
            
            if save_timezone_config(new_config):
                flash('✅ Timezone ayarları başarıyla güncellendi!', 'success')
                print(f"🕐 Timezone güncellendi: {timezone}")
            else:
                flash('❌ Timezone ayarları kaydedilemedi!', 'danger')
                
        except Exception as e:
            flash(f'❌ Timezone ayarları güncellenirken hata oluştu: {str(e)}', 'danger')
            print(f"❌ Timezone ayarları güncelleme hatası: {e}")
    
    # Mevcut ayarları yükle
    current_config = load_timezone_config()
    popular_timezones = get_popular_timezones()
    all_timezones = get_all_timezones()
    
    return render_template('timezone_settings.html', 
                         config=current_config,
                         popular_timezones=popular_timezones,
                         all_timezones=all_timezones)

@app.route('/debug/mail')
@login_required
def debug_mail():
    """Mail konfigürasyonunu debug etmek için"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Bu sayfaya erişim yetkiniz yok.'}), 403
    
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
    if current_user.role != 'admin':
        return jsonify({'error': 'Bu sayfaya erişim yetkiniz yok.'}), 403
    
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
            <p>Gönderim zamanı: ''' + format_date_time(datetime.now()) + '''</p>
            '''
        )
        mail.send(msg)
        return jsonify({'status': 'success', 'message': f'Test mail gönderildi: {current_user.email}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Mail gönderme hatası: {str(e)}'})

# Görev silme (admin ve görev sahibi manager)
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü - admin veya görev oluşturan kişi silebilir
    if current_user.role != 'admin' and task.created_by != current_user.id:
        flash('Bu görevi silme yetkiniz yok!')
        return redirect(url_for('index'))
    
    try:
        # Görev başlığını flash mesajı için sakla
        task_title = task.title
        
        # İlişkili yorumları sil
        Comment.query.filter_by(task_id=task_id).delete()
        
        # Görev atamalarını temizle (Many-to-Many ilişki otomatik temizlenir)
        task.assignees.clear()
        
        # Görevi sil
        db.session.delete(task)
        db.session.commit()
        
        flash(f'Görev "{task_title}" başarıyla silindi!')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Görev silinirken hata oluştu: {str(e)}')
    
    return redirect(url_for('index'))

# Görev tamamlama
@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü - admin, manager veya görevde atanmış kişi tamamlayabilir
    if (current_user.role not in ['admin', 'manager'] and 
        current_user not in task.assignees):
        flash('Bu görevi tamamlama yetkiniz yok!')
        return redirect(url_for('index'))
    
    try:
        # Görevi tamamlandı olarak işaretle
        task.status = 'completed'
        db.session.commit()
        
        flash(f'Görev "{task.title}" tamamlandı olarak işaretlendi!')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Görev tamamlanırken hata oluştu: {str(e)}')
    
    return jsonify({'success': True})

@app.route('/get_task_description/<int:task_id>', methods=['GET'])
@login_required
def get_task_description(task_id):
    """Görev açıklamasını getir - Sadece görev oluşturan kişi görebilir"""
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü - sadece görev oluşturan kişi görebilir
    if task.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Bu görevin açıklamasını görme yetkiniz yok!'})
    
    return jsonify({
        'success': True,
        'description': task.description or ''
    })

@app.route('/edit_task_description/<int:task_id>', methods=['POST'])
@login_required
def edit_task_description(task_id):
    """Görev açıklamasını düzenle - Sadece görev oluşturan kişi düzenleyebilir"""
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü - sadece görev oluşturan kişi düzenleyebilir
    if task.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Bu görevin açıklamasını düzenleme yetkiniz yok!'})
    
    try:
        new_description = request.json.get('description', '').strip()
        
        # Açıklamayı güncelle
        task.description = new_description
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Görev açıklaması güncellendi!',
            'new_description': new_description
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Açıklama güncellenirken hata oluştu: {str(e)}'})

@app.route('/save_checkbox_state/<int:task_id>', methods=['POST'])
@login_required
def save_checkbox_state(task_id):
    """Checkbox durumlarını kaydet - Atanan kişiler ve görev oluşturan erişebilir"""
    task = Task.query.get_or_404(task_id)
    
    # Yetki kontrolü - görev oluşturan veya atanan kişiler erişebilir
    if (task.created_by != current_user.id and 
        current_user not in task.assignees):
        return jsonify({'success': False, 'message': 'Bu görevin checkbox durumlarını değiştirme yetkiniz yok!'})
    
    try:
        # Frontend'den gelen HTML'i al
        updated_description = request.json.get('description', '').strip()
        
        # Açıklamayı güncelle (checkbox durumları ile birlikte)
        task.description = updated_description
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Checkbox durumları kaydedildi!',
            'updated_by': current_user.username
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Checkbox durumları kaydedilemedi: {str(e)}'})

# =============================================================================
# RAPOR SİSTEMİ
# =============================================================================

# Raporlar ana sayfası
@app.route('/reports')
@login_required
def reports():
    """Rapor listesi sayfası"""
    # Kullanıcının kendi raporları
    my_reports = Report.query.filter_by(author_id=current_user.id).order_by(Report.report_date.desc()).all()
    
    # Kullanıcıya paylaşılan raporlar
    shared_reports = Report.query.join(report_shares).filter(report_shares.c.user_id == current_user.id).order_by(Report.report_date.desc()).all()
    
    # Admin ve manager'lar tüm raporları görebilir
    if current_user.role in ['admin', 'manager']:
        if current_user.role == 'admin':
            all_reports = Report.query.filter_by(is_private=False).order_by(Report.report_date.desc()).all()
        else:
            # Manager kendi departmanındaki raporları görebilir
            dept_users = User.query.filter_by(department=current_user.department).all()
            user_ids = [user.id for user in dept_users]
            all_reports = Report.query.filter(Report.author_id.in_(user_ids), Report.is_private==False).order_by(Report.report_date.desc()).all()
    else:
        all_reports = []
    
    return render_template('reports.html', 
                         my_reports=my_reports, 
                         shared_reports=shared_reports,
                         all_reports=all_reports)

# Yeni rapor oluşturma
@app.route('/reports/create', methods=['GET', 'POST'])
@login_required
def create_report():
    """Yeni rapor oluşturma"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        report_date = request.form.get('report_date')
        is_private = request.form.get('is_private') == 'on'
        shared_users = request.form.getlist('shared_users')  # Paylaşılacak kullanıcılar
        
        if not title or not content or not report_date:
            flash('Tüm alanlar zorunludur!', 'error')
            return redirect(url_for('create_report'))
        
        try:
            # Tarih dönüşümü
            report_date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
            
            # Yeni rapor oluştur
            report = Report(
                title=title,
                content=content,
                report_date=report_date_obj,
                is_private=is_private,
                author_id=current_user.id
            )
            
            db.session.add(report)
            db.session.flush()  # ID'yi almak için flush
            
            # Paylaşım işlemi
            if shared_users:
                for user_id in shared_users:
                    if user_id and user_id != str(current_user.id):  # Kendisi ile paylaşmasın
                        try:
                            user_id_int = int(user_id)
                            # Kullanıcının var olup olmadığını kontrol et
                            if User.query.get(user_id_int):
                                db.session.execute(
                                    report_shares.insert().values(
                                        report_id=report.id,
                                        user_id=user_id_int
                                    )
                                )
                        except (ValueError, TypeError):
                            continue
            
            db.session.commit()
            
            flash('Rapor başarıyla oluşturuldu!', 'success')
            return redirect(url_for('reports'))
            
        except ValueError:
            flash('Geçersiz tarih formatı!', 'error')
            return redirect(url_for('create_report'))
        except Exception as e:
            flash(f'Hata: {str(e)}', 'error')
            return redirect(url_for('create_report'))
    
    # GET request - mevcut kullanıcıları getir
    users = User.query.filter(User.id != current_user.id).order_by(User.username).all()
    return render_template('create_report.html', users=users)

# Rapor detay sayfası
@app.route('/reports/<int:report_id>')
@login_required
def report_detail(report_id):
    """Rapor detay sayfası"""
    report = Report.query.get_or_404(report_id)
    
    # Yetki kontrolü
    can_view = (report.author_id == current_user.id or 
               current_user in report.shared_with or 
               (current_user.role == 'admin') or
               (current_user.role == 'manager' and report.author.department == current_user.department and not report.is_private))
    
    if not can_view:
        flash('Bu raporu görüntüleme yetkiniz yok!', 'error')
        return redirect(url_for('reports'))
    
    # Raporu okundu olarak işaretle
    report.mark_as_read(current_user)
    
    # Yorumları getir
    comments = ReportComment.query.filter_by(report_id=report_id).order_by(ReportComment.created_at.desc()).all()
    
    # Paylaşılabilen kullanıcıları getir (aynı departmandaki kullanıcılar)
    if current_user.department:
        shareable_users = User.query.filter(
            User.department == current_user.department,
            User.id != current_user.id
        ).all()
    else:
        shareable_users = []
    
    return render_template('report_detail.html', 
                         report=report, 
                         comments=comments,
                         shareable_users=shareable_users)

# Rapor paylaşma
@app.route('/reports/<int:report_id>/share', methods=['POST'])
@login_required
def share_report(report_id):
    """Raporu belirli kullanıcılarla paylaş"""
    report = Report.query.get_or_404(report_id)
    
    # Yetki kontrolü - sadece rapor sahibi paylaşabilir
    if report.author_id != current_user.id:
        flash('Bu raporu paylaşma yetkiniz yok!', 'error')
        return redirect(url_for('report_detail', report_id=report_id))
    
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        flash('Lütfen en az bir kullanıcı seçin!', 'error')
        return redirect(url_for('report_detail', report_id=report_id))
    
    try:
        # Mevcut paylaşımları temizle
        report.shared_with.clear()
        
        # Yeni paylaşımları ekle
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user.department == current_user.department:
                report.shared_with.append(user)
        
        db.session.commit()
        flash('Rapor başarıyla paylaşıldı!', 'success')
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('report_detail', report_id=report_id))

# Rapor yorumu ekleme
@app.route('/reports/<int:report_id>/comment', methods=['POST'])
@login_required
def add_report_comment(report_id):
    """Rapor yorumu ekleme"""
    report = Report.query.get_or_404(report_id)
    
    # Yetki kontrolü
    can_comment = (report.author_id == current_user.id or 
                  current_user in report.shared_with or 
                  (current_user.role == 'admin') or
                  (current_user.role == 'manager' and report.author.department == current_user.department and not report.is_private))
    
    if not can_comment:
        flash('Bu raporu yorumlama yetkiniz yok!', 'error')
        return redirect(url_for('reports'))
    
    content = request.form.get('content')
    
    if not content:
        flash('Yorum içeriği boş olamaz!', 'error')
        return redirect(url_for('report_detail', report_id=report_id))
    
    try:
        comment = ReportComment(
            content=content,
            report_id=report_id,
            user_id=current_user.id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Yorum başarıyla eklendi!', 'success')
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('report_detail', report_id=report_id))

# Rapor düzenleme
@app.route('/reports/<int:report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    """Rapor düzenleme"""
    report = Report.query.get_or_404(report_id)
    
    # Yetki kontrolü - sadece rapor sahibi düzenleyebilir
    if report.author_id != current_user.id:
        flash('Bu raporu düzenleme yetkiniz yok!', 'error')
        return redirect(url_for('report_detail', report_id=report_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        report_date = request.form.get('report_date')
        is_private = request.form.get('is_private') == 'on'
        shared_users = request.form.getlist('shared_users')  # Paylaşılacak kullanıcılar
        
        if not title or not content or not report_date:
            flash('Tüm alanlar zorunludur!', 'error')
            return redirect(url_for('edit_report', report_id=report_id))
        
        try:
            # Tarih dönüşümü
            report_date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
            
            # Raporu güncelle
            report.title = title
            report.content = content
            report.report_date = report_date_obj
            report.is_private = is_private
            report.updated_at = datetime.utcnow()
            
            # Mevcut paylaşımları sil
            db.session.execute(
                report_shares.delete().where(report_shares.c.report_id == report_id)
            )
            
            # Yeni paylaşımları ekle
            if shared_users:
                for user_id in shared_users:
                    if user_id and user_id != str(current_user.id):  # Kendisi ile paylaşmasın
                        try:
                            user_id_int = int(user_id)
                            # Kullanıcının var olup olmadığını kontrol et
                            if User.query.get(user_id_int):
                                db.session.execute(
                                    report_shares.insert().values(
                                        report_id=report_id,
                                        user_id=user_id_int
                                    )
                                )
                        except (ValueError, TypeError):
                            continue
            
            db.session.commit()
            
            flash('Rapor başarıyla güncellendi!', 'success')
            return redirect(url_for('report_detail', report_id=report_id))
            
        except ValueError:
            flash('Geçersiz tarih formatı!', 'error')
            return redirect(url_for('edit_report', report_id=report_id))
        except Exception as e:
            flash(f'Hata: {str(e)}', 'error')
            return redirect(url_for('edit_report', report_id=report_id))
    
    # GET request - mevcut kullanıcıları ve paylaşımları getir
    users = User.query.filter(User.id != current_user.id).order_by(User.username).all()
    shared_user_ids = [user.id for user in report.shared_with]
    
    return render_template('edit_report.html', report=report, users=users, shared_user_ids=shared_user_ids)

# Rapor silme
@app.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    """Rapor silme"""
    report = Report.query.get_or_404(report_id)
    
    # Yetki kontrolü - sadece rapor sahibi veya admin silebilir
    if report.author_id != current_user.id and current_user.role != 'admin':
        flash('Bu raporu silme yetkiniz yok!', 'error')
        return redirect(url_for('report_detail', report_id=report_id))
    
    try:
        # İlişkili kayıtları temizle: yorumlar, paylaşımlar, okuma kayıtları
        db.session.query(ReportComment).filter_by(report_id=report_id).delete()
        db.session.execute(report_shares.delete().where(report_shares.c.report_id == report_id))
        db.session.execute(report_reads.delete().where(report_reads.c.report_id == report_id))

        # Raporu sil
        db.session.delete(report)
        db.session.commit()
        
        flash('Rapor başarıyla silindi!', 'success')
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('reports'))

# =============================================================================
# Navbar bildirimleri için API endpoint'leri
@app.route('/api/tasks_notifications')
@login_required
def api_tasks_notifications():
    """Görevler için bildirim sayısını döndürür - Optimize edilmiş version"""
    try:
        today = datetime.now().date()
        yesterday = datetime.now() - timedelta(days=1)
        
        # Memory optimization: User'ın assigned_tasks ile tek query'de al
        user_tasks = current_user.assigned_tasks.filter(Task.status != 'completed').all()
        
        # In-memory filtering (database query yerine)
        overdue_count = 0
        today_urgent_count = 0
        new_tasks_count = 0
        
        for task in user_tasks:
            # Tarih normalizasyonu
            due_date_date = None
            if task.due_date:
                try:
                    due_date_date = task.due_date.date()
                except Exception:
                    due_date_date = task.due_date

            # Gecikmiş görevler
            if due_date_date and due_date_date < today:
                overdue_count += 1
                continue
            
            # Bugün için acil görevler  
            if due_date_date and due_date_date == today and task.priority == 'urgent':
                today_urgent_count += 1
                continue
                
            # Yeni atanmış görevler (son 24 saat)
            if task.created_at >= yesterday and task.status == 'pending':
                new_tasks_count += 1
        
        total_notifications = overdue_count + today_urgent_count + new_tasks_count
        
        return jsonify({
            'total': total_notifications,
            'overdue': overdue_count,
            'today_urgent': today_urgent_count,
            'new_tasks': new_tasks_count
        })
        
    except Exception as e:
        print(f"⚠️ Notification API error: {e}")
        return jsonify({
            'total': 0,
            'overdue': 0,
            'today_urgent': 0,
            'new_tasks': 0
        })

@app.route('/api/reports_notifications')
@login_required
def api_reports_notifications():
    """Raporlar için bildirim sayısını döndürür"""
    # Kullanıcının paylaşılan raporları
    shared_reports = db.session.query(Report).join(
        report_shares, Report.id == report_shares.c.report_id
    ).filter(
        report_shares.c.user_id == current_user.id,
        Report.author_id != current_user.id
    ).count()
    
    # Yeni yorumlar (son 24 saat)
    yesterday = datetime.now() - timedelta(days=1)
    user_reports = Report.query.filter_by(author_id=current_user.id).all()
    new_comments = 0
    
    for report in user_reports:
        comment_count = ReportComment.query.filter(
            ReportComment.report_id == report.id,
            ReportComment.author_id != current_user.id,
            ReportComment.created_at >= yesterday
        ).count()
        new_comments += comment_count
    
    total_notifications = shared_reports + new_comments
    
    return jsonify({
        'count': total_notifications,
        'shared_reports': shared_reports,
        'new_comments': new_comments
    })

# =============================================================================
if __name__ == '__main__':
    import os
    import time
    import sys
    
    # Memory usage monitoring  
    def print_memory_usage():
        """Memory kullanımını yazdır"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"🧠 Memory usage: {memory_mb:.1f} MB")
        except ImportError:
            print("📊 psutil not available for memory monitoring")
    
    print_memory_usage()
    
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
    print_memory_usage()  # Memory kullanımını başlangıçta da göster
    app.run(debug=debug, host='0.0.0.0', port=port)
