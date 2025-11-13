from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    bookings_as_customer = db.relationship('Booking', foreign_keys='Booking.customer_id', backref='customer', lazy=True)
    trust_score = db.relationship('TrustScore', backref='user', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'

class Plumber(db.Model):
    __tablename__ = 'plumbers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialty = db.Column(db.String(200))
    location = db.Column(db.String(200))
    hourly_rate = db.Column(db.Float)
    experience_years = db.Column(db.Integer)
    bio = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('plumber_profile', uselist=False))
    bookings = db.relationship('Booking', foreign_keys='Booking.plumber_id', backref='plumber', lazy=True)
    trust_score = db.relationship('TrustScore', backref='plumber', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Plumber {self.id} - {self.specialty}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'), nullable=False)
    service_description = db.Column(db.Text, nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')
    price = db.Column(db.Float)
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

class TrustScore(db.Model):
    __tablename__ = 'trust_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'), unique=True)
    overall_score = db.Column(db.Float, default=50.0)
    completion_rate = db.Column(db.Float, default=0.0)
    review_authenticity = db.Column(db.Float, default=50.0)
    response_time_score = db.Column(db.Float, default=50.0)
    dispute_count = db.Column(db.Integer, default=0)
    anomaly_score = db.Column(db.Float, default=0.0)
    total_transactions = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrustScore {self.id} - Score: {self.overall_score}>'

class FraudAlert(db.Model):
    __tablename__ = 'fraud_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    alert_type = db.Column(db.String(100), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    flagged_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='fraud_alerts')
    
    def __repr__(self):
        return f'<FraudAlert {self.id} - {self.alert_type} - Risk: {self.risk_score}>'

class LocalModelUpdate(db.Model):
    __tablename__ = 'local_model_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    model_version = db.Column(db.Integer, nullable=False)
    update_data = db.Column(db.Text, nullable=False)
    data_samples_count = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    aggregated = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<LocalModelUpdate {self.id} - Version: {self.model_version}>'

class GlobalModel(db.Model):
    __tablename__ = 'global_models'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, unique=True, nullable=False)
    model_data = db.Column(db.Text, nullable=False)
    accuracy = db.Column(db.Float)
    updates_aggregated = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<GlobalModel Version: {self.version} - Accuracy: {self.accuracy}>'
