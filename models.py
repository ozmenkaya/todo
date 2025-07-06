from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Many-to-Many ilişki tablosu (görev atamaları için)
task_assignments = db.Table('task_assignments',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)  # PostgreSQL için artırıldı
    password_hash = db.Column(db.String(255), nullable=False)  # PostgreSQL için artırıldı  
    role = db.Column(db.String(20), default='employee')  # 'admin', 'manager', 'employee'
    department = db.Column(db.String(100))  # PostgreSQL için artırıldı
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    title = db.Column(db.String(500), nullable=False)  # PostgreSQL için artırıldı
    description = db.Column(db.Text)
    reminder_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # İlişki
    user = db.relationship('User', backref='reminders')
