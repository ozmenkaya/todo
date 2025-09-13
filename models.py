from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Many-to-Many ilişki tablosu (görev atamaları için)
task_assignments = db.Table('task_assignments',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Many-to-Many ilişki tablosu (rapor paylaşımları için)
report_shares = db.Table('report_shares',
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('shared_at', db.DateTime, default=datetime.utcnow)
)

# Görev okunma durumu takip tablosu
task_reads = db.Table('task_reads',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('read_at', db.DateTime, default=datetime.utcnow),
    db.Column('last_read_at', db.DateTime, default=datetime.utcnow)
)

# Rapor okunma durumu takip tablosu
report_reads = db.Table('report_reads',
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('read_at', db.DateTime, default=datetime.utcnow),
    db.Column('last_read_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)  # PostgreSQL için artırıldı
    password_hash = db.Column(db.String(255), nullable=False)  # PostgreSQL için artırıldı  
    role = db.Column(db.String(20), default='employee')  # 'admin', 'manager', 'employee'
    department = db.Column(db.String(100))  # PostgreSQL için artırıldı
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # OneSignal Notification Settings - Nullable for backward compatibility
    push_notifications_enabled = db.Column(db.Boolean, default=True, nullable=True)
    task_assignment_notifications = db.Column(db.Boolean, default=True, nullable=True)
    task_completion_notifications = db.Column(db.Boolean, default=True, nullable=True)
    reminder_notifications = db.Column(db.Boolean, default=True, nullable=True)
    report_notifications = db.Column(db.Boolean, default=True, nullable=True)
    onesignal_player_id = db.Column(db.String(255), nullable=True)  # OneSignal Player ID
    
    # İlişkiler
    assigned_tasks = db.relationship('Task', secondary=task_assignments, back_populates='assignees', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', lazy='dynamic')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)  # PostgreSQL için artırıldı
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
    readers = db.relationship('User', secondary=task_reads, backref='read_tasks')
    
    def is_read_by(self, user):
        """Belirli bir kullanıcı tarafından okundu mu kontrol et"""
        return db.session.query(task_reads).filter_by(task_id=self.id, user_id=user.id).first() is not None
    
    def mark_as_read(self, user):
        """Görevi okundu olarak işaretle"""
        existing_read = db.session.query(task_reads).filter_by(task_id=self.id, user_id=user.id).first()
        if existing_read:
            # Mevcut okunma kaydını güncelle
            db.session.execute(
                task_reads.update()
                .where(task_reads.c.task_id == self.id)
                .where(task_reads.c.user_id == user.id)
                .values(last_read_at=datetime.utcnow())
            )
        else:
            # Yeni okunma kaydı ekle
            db.session.execute(
                task_reads.insert().values(task_id=self.id, user_id=user.id)
            )
        db.session.commit()
    
    def get_read_info(self, user):
        """Kullanıcı için okunma bilgilerini getir"""
        read_info = db.session.query(task_reads).filter_by(task_id=self.id, user_id=user.id).first()
        if read_info:
            return {
                'is_read': True,
                'read_at': read_info.read_at,
                'last_read_at': read_info.last_read_at
            }
        return {'is_read': False}

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişkiler
    # Görev silindiğinde yorumları da sil (ORM seviyesinde)
    task = db.relationship(
        'Task',
        backref=db.backref('comments', cascade='all, delete-orphan')
    )
    user = db.relationship('User', backref='comments')

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)  # PostgreSQL için artırıldı
    description = db.Column(db.Text)
    reminder_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişki
    user = db.relationship('User', backref='reminders')

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    report_date = db.Column(db.Date, nullable=False)  # Hangi güne ait rapor
    is_private = db.Column(db.Boolean, default=True)  # Özel mi yoksa herkese açık mı
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Key
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişkiler
    author = db.relationship('User', backref='authored_reports')
    shared_with = db.relationship('User', secondary=report_shares, backref='shared_reports')
    readers = db.relationship('User', secondary=report_reads, backref='read_reports')
    
    def is_read_by(self, user):
        """Belirli bir kullanıcı tarafından okundu mu kontrol et"""
        return db.session.query(report_reads).filter_by(report_id=self.id, user_id=user.id).first() is not None
    
    def mark_as_read(self, user):
        """Raporu okundu olarak işaretle"""
        existing_read = db.session.query(report_reads).filter_by(report_id=self.id, user_id=user.id).first()
        if existing_read:
            # Mevcut okunma kaydını güncelle
            db.session.execute(
                report_reads.update()
                .where(report_reads.c.report_id == self.id)
                .where(report_reads.c.user_id == user.id)
                .values(last_read_at=datetime.utcnow())
            )
        else:
            # Yeni okunma kaydı ekle
            db.session.execute(
                report_reads.insert().values(report_id=self.id, user_id=user.id)
            )
        db.session.commit()
    
    def get_read_info(self, user):
        """Kullanıcı için okunma bilgilerini getir"""
        read_info = db.session.query(report_reads).filter_by(report_id=self.id, user_id=user.id).first()
        if read_info:
            return {
                'is_read': True,
                'read_at': read_info.read_at,
                'last_read_at': read_info.last_read_at
            }
        return {'is_read': False}

class ReportComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişkiler
    # Rapor silindiğinde yorumları da sil (ORM seviyesinde)
    report = db.relationship(
        'Report',
        backref=db.backref('comments', cascade='all, delete-orphan')
    )
    user = db.relationship('User', backref='report_comments')
