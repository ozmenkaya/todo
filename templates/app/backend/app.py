#!/usr/bin/env python3
"""
Flask Backend for Company Task Management System
Mobile PWA Backend API Server

This Flask application provides REST API endpoints for:
- User authentication and management
- Task management (CRUD operations)
- Report management and sharing
- Reminder system
- Real-time notifications

Features:
- Session-based authentication
- CORS support for mobile PWA
- SQLite database for development
- RESTful API design
- Error handling and validation
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration based on environment
if os.getenv('FLASK_ENV') == 'production':
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'production-secret-key')
    app.config['DEBUG'] = False
    cors_origins = os.getenv('CORS_ORIGINS', '').split(',')
else:
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['DEBUG'] = True
    cors_origins = ['http://localhost:3005', 'http://localhost:3004', 'http://localhost:3000']

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///company_tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure CORS for mobile PWA
CORS(app, 
     origins=cors_origins,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin, manager, employee
    department = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator')
    created_reports = db.relationship('Report', foreign_keys='Report.created_by', backref='creator')
    reminders = db.relationship('Reminder', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'department': self.department,
            'created_at': self.created_at.isoformat() + 'Z'
        }

# Association table for many-to-many relationship between tasks and users
task_assignees = db.Table('task_assignees',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

# Association table for many-to-many relationship between reports and users
report_shares = db.Table('report_shares',
    db.Column('report_id', db.Integer, db.ForeignKey('reports.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # urgent, high, medium, low
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Many-to-many relationship with users (assignees)
    assignees = db.relationship('User', secondary=task_assignees, backref='assigned_tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_by': self.created_by,
            'assigned_to': [user.id for user in self.assignees],
            'due_date': self.due_date.isoformat() + 'Z' if self.due_date else None,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None,
            'creator': self.creator.to_dict(),
            'assignees': [user.to_dict() for user in self.assignees],
            'is_read': True  # Default for now
        }

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with users (shared with)
    shared_users = db.relationship('User', secondary=report_shares, backref='shared_reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_by': self.created_by,
            'shared_with': [user.id for user in self.shared_users],
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'creator': self.creator.to_dict(),
            'shared_users': [user.to_dict() for user in self.shared_users],
            'is_read': True  # Default for now
        }

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reminder_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'reminder_time': self.reminder_time.isoformat() + 'Z',
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() + 'Z',
            'is_completed': self.is_completed
        }

# Helper function to get current user
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# Helper function to require authentication
def require_auth():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    return user

# Authentication Routes
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            logger.info(f"User {username} logged in successfully")
            return jsonify(user.to_dict()), 200
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/current_user', methods=['GET'])
def current_user():
    user = get_current_user()
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'error': 'Not authenticated'}), 401

# Task Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    user = require_auth()
    if isinstance(user, tuple):  # Error response
        return user
    
    # Get all tasks where user is creator or assignee
    tasks = Task.query.filter(
        (Task.created_by == user.id) | 
        (Task.assignees.contains(user))
    ).order_by(Task.created_at.desc()).all()
    
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    task = Task.query.get_or_404(task_id)
    
    # Check if user has access to this task
    if task.created_by != user.id and user not in task.assignees:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(task.to_dict()), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    try:
        data = request.get_json()
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            created_by=user.id,
            due_date=datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data.get('due_date') else None
        )
        
        # Add assignees
        if 'assigned_to' in data:
            assignees = User.query.filter(User.id.in_(data['assigned_to'])).all()
            task.assignees = assignees
        
        db.session.add(task)
        db.session.commit()
        
        logger.info(f"Task created: {task.title} by user {user.username}")
        return jsonify(task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task creation error: {str(e)}")
        return jsonify({'error': 'Failed to create task'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    task = Task.query.get_or_404(task_id)
    
    # Check if user has permission to update this task
    if task.created_by != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
        
        # Update assignees
        if 'assigned_to' in data:
            assignees = User.query.filter(User.id.in_(data['assigned_to'])).all()
            task.assignees = assignees
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Task updated: {task.title} by user {user.username}")
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task update error: {str(e)}")
        return jsonify({'error': 'Failed to update task'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    task = Task.query.get_or_404(task_id)
    
    # Check if user has permission to delete this task
    if task.created_by != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f"Task deleted: {task.title} by user {user.username}")
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete task'}), 500

@app.route('/api/tasks/<int:task_id>/mark_read', methods=['POST'])
def mark_task_as_read(task_id):
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    # For now, just return success
    # In a real implementation, you might store read status in a separate table
    return jsonify({'message': 'Task marked as read'}), 200

# Report Routes
@app.route('/api/reports', methods=['GET'])
def get_reports():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    # Get all reports where user is creator or shared with
    reports = Report.query.filter(
        (Report.created_by == user.id) | 
        (Report.shared_users.contains(user))
    ).order_by(Report.created_at.desc()).all()
    
    return jsonify([report.to_dict() for report in reports]), 200

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    report = Report.query.get_or_404(report_id)
    
    # Check if user has access to this report
    if report.created_by != user.id and user not in report.shared_users:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(report.to_dict()), 200

@app.route('/api/reports', methods=['POST'])
def create_report():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    try:
        data = request.get_json()
        
        report = Report(
            title=data['title'],
            content=data['content'],
            created_by=user.id
        )
        
        # Add shared users
        if 'shared_with' in data:
            shared_users = User.query.filter(User.id.in_(data['shared_with'])).all()
            report.shared_users = shared_users
        
        db.session.add(report)
        db.session.commit()
        
        logger.info(f"Report created: {report.title} by user {user.username}")
        return jsonify(report.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Report creation error: {str(e)}")
        return jsonify({'error': 'Failed to create report'}), 500

@app.route('/api/reports/<int:report_id>/mark_read', methods=['POST'])
def mark_report_as_read(report_id):
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    # For now, just return success
    return jsonify({'message': 'Report marked as read'}), 200

# Reminder Routes
@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    reminders = Reminder.query.filter_by(user_id=user.id).order_by(Reminder.reminder_time.desc()).all()
    return jsonify([reminder.to_dict() for reminder in reminders]), 200

@app.route('/api/today_reminders', methods=['GET'])
def get_today_reminders():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    # Get reminders for today
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    reminders = Reminder.query.filter(
        Reminder.user_id == user.id,
        Reminder.reminder_time >= today,
        Reminder.reminder_time < tomorrow,
        Reminder.is_completed == False
    ).order_by(Reminder.reminder_time).all()
    
    return jsonify([reminder.to_dict() for reminder in reminders]), 200

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    try:
        data = request.get_json()
        
        reminder = Reminder(
            title=data['title'],
            description=data.get('description', ''),
            reminder_time=datetime.fromisoformat(data['reminder_time'].replace('Z', '+00:00')),
            user_id=user.id
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        logger.info(f"Reminder created: {reminder.title} by user {user.username}")
        return jsonify(reminder.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Reminder creation error: {str(e)}")
        return jsonify({'error': 'Failed to create reminder'}), 500

# User Routes
@app.route('/api/users', methods=['GET'])
def get_users():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

# Notification Routes
@app.route('/api/notification_counts', methods=['GET'])
def get_notification_counts():
    user = require_auth()
    if isinstance(user, tuple):
        return user
    
    # Count unread items (simplified for demo)
    task_count = Task.query.filter(
        (Task.created_by == user.id) | (Task.assignees.contains(user)),
        Task.status != 'completed'
    ).count()
    
    reminder_count = Reminder.query.filter(
        Reminder.user_id == user.id,
        Reminder.is_completed == False,
        Reminder.reminder_time >= datetime.now().date(),
        Reminder.reminder_time < datetime.now().date() + timedelta(days=1)
    ).count()
    
    report_count = Report.query.filter(
        (Report.created_by == user.id) | (Report.shared_users.contains(user))
    ).count()
    
    return jsonify({
        'tasks': task_count,
        'reminders': reminder_count,
        'reports': report_count
    }), 200

# Initialize database and create sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@company.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                department='IT'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create regular user
            user = User(
                username='user',
                email='user@company.com',
                first_name='John',
                last_name='Doe',
                role='employee',
                department='Sales'
            )
            user.set_password('user123')
            db.session.add(user)
            
            db.session.commit()
            
            # Create sample tasks
            task1 = Task(
                title='Proje planını hazırla',
                description='Q1 2025 için detaylı proje planı hazırlanması gerekiyor.',
                status='in_progress',
                priority='high',
                created_by=admin.id,
                due_date=datetime.now() + timedelta(days=5)
            )
            task1.assignees = [admin, user]
            
            task2 = Task(
                title='Müşteri toplantısı',
                description='ABC şirketi ile ürün demo toplantısı',
                status='pending',
                priority='urgent',
                created_by=admin.id,
                due_date=datetime.now() + timedelta(days=1)
            )
            task2.assignees = [admin]
            
            task3 = Task(
                title='Rapor hazırla',
                description='Aylık performans raporu',
                status='completed',
                priority='medium',
                created_by=admin.id,
                due_date=datetime.now() - timedelta(days=1),
                completed_at=datetime.now() - timedelta(hours=2)
            )
            task3.assignees = [admin]
            
            db.session.add_all([task1, task2, task3])
            
            # Create sample reports
            report1 = Report(
                title='Haftalık İlerleme Raporu',
                content='Bu hafta tamamlanan işler ve gelecek hafta planları...',
                created_by=admin.id
            )
            report1.shared_users = [admin, user]
            
            report2 = Report(
                title='Müşteri Memnuniyet Anketi',
                content='Son dönemde yapılan müşteri memnuniyet anket sonuçları...',
                created_by=admin.id
            )
            report2.shared_users = [admin]
            
            db.session.add_all([report1, report2])
            
            # Create sample reminders
            reminder1 = Reminder(
                title='Toplantı hatırlatması',
                description='Saat 14:00\'te ekip toplantısı',
                reminder_time=datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
                user_id=admin.id
            )
            
            reminder2 = Reminder(
                title='Rapor teslimi',
                description='Aylık raporu teslim etmeyi unutma',
                reminder_time=datetime.now().replace(hour=17, minute=0, second=0, microsecond=0),
                user_id=admin.id
            )
            
            db.session.add_all([reminder1, reminder2])
            db.session.commit()
            
            logger.info("Database initialized with sample data")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start the server
    logger.info("Starting Flask backend server on http://localhost:5005")
    app.run(host='0.0.0.0', port=5005, debug=True)
