from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db, User, Plumber, Booking, TrustScore, FraudAlert, LocalModelUpdate, GlobalModel
from ml_models.fraud_detector import fraud_detector
from ml_models.federated_orchestrator import federated_orchestrator
from ml_models.trust_scorer import trust_scorer
from config import Config
from datetime import datetime, timedelta
from functools import wraps
import json
import numpy as np
import random

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Custom Jinja2 filter to convert UTC to IST
@app.template_filter('to_ist')
def to_ist(utc_dt):
    """Convert UTC datetime to IST (UTC+5:30)"""
    if utc_dt is None:
        return ''
    ist_offset = timedelta(hours=5, minutes=30)
    ist_dt = utc_dt + ist_offset
    return ist_dt.strftime('%Y-%m-%d %H:%M IST')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role and current_user.role != 'admin':
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, password_hash=hashed_password, name=name, role=role)
        db.session.add(user)
        db.session.commit()
        
        trust_score = TrustScore(user_id=user.id)
        db.session.add(trust_score)
        
        if role == 'plumber':
            plumber = Plumber(
                user_id=user.id,
                specialty=request.form.get('specialty', 'General Plumbing'),
                location=request.form.get('location', 'Not specified'),
                hourly_rate=float(request.form.get('hourly_rate', 50)),
                experience_years=int(request.form.get('experience_years', 1))
            )
            db.session.add(plumber)
            plumber_trust = TrustScore(plumber_id=plumber.id)
            db.session.add(plumber_trust)
        
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'customer':
        return redirect(url_for('customer_dashboard'))
    elif current_user.role == 'plumber':
        return redirect(url_for('plumber_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('index'))

@app.route('/customer/dashboard')
@login_required
@role_required('customer')
def customer_dashboard():
    bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(Booking.created_at.desc()).all()
    trust_score = TrustScore.query.filter_by(user_id=current_user.id).first()
    plumbers = Plumber.query.filter_by(available=True).all()
    return render_template('customer_dashboard.html', bookings=bookings, trust_score=trust_score, plumbers=plumbers)

@app.route('/plumber/dashboard')
@login_required
@role_required('plumber')
def plumber_dashboard():
    plumber = Plumber.query.filter_by(user_id=current_user.id).first()
    if not plumber:
        flash('Plumber profile not found.', 'danger')
        return redirect(url_for('index'))
    
    bookings = Booking.query.filter_by(plumber_id=plumber.id).order_by(Booking.created_at.desc()).all()
    trust_score = TrustScore.query.filter_by(plumber_id=plumber.id).first()
    
    return render_template('plumber_dashboard.html', plumber=plumber, bookings=bookings, trust_score=trust_score)

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    total_users = User.query.count()
    total_plumbers = Plumber.query.count()
    total_bookings = Booking.query.count()
    completed_bookings = Booking.query.filter_by(status='completed').count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    
    fraud_alerts = FraudAlert.query.filter_by(status='pending').order_by(FraudAlert.flagged_at.desc()).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get all reviews (completed bookings with ratings)
    all_reviews = Booking.query.filter(Booking.rating.isnot(None)).order_by(Booking.created_at.desc()).all()
    
    # Get all plumber profiles with their stats
    plumbers = Plumber.query.all()
    plumber_stats = []
    for plumber in plumbers:
        plumber_bookings = Booking.query.filter_by(plumber_id=plumber.id).count()
        plumber_completed = Booking.query.filter_by(plumber_id=plumber.id, status='completed').count()
        plumber_reviews = Booking.query.filter_by(plumber_id=plumber.id).filter(Booking.rating.isnot(None)).all()
        avg_rating = sum([r.rating for r in plumber_reviews]) / len(plumber_reviews) if plumber_reviews else 0
        trust = TrustScore.query.filter_by(plumber_id=plumber.id).first()
        
        plumber_stats.append({
            'plumber': plumber,
            'total_bookings': plumber_bookings,
            'completed_bookings': plumber_completed,
            'avg_rating': round(avg_rating, 2),
            'review_count': len(plumber_reviews),
            'trust_score': trust.overall_score if trust else 50
        })
    
    # Get all customer profiles
    customers = User.query.filter_by(role='customer').all()
    customer_stats = []
    for customer in customers:
        customer_bookings = Booking.query.filter_by(customer_id=customer.id).count()
        customer_completed = Booking.query.filter_by(customer_id=customer.id, status='completed').count()
        trust = TrustScore.query.filter_by(user_id=customer.id).first()
        
        customer_stats.append({
            'customer': customer,
            'total_bookings': customer_bookings,
            'completed_bookings': customer_completed,
            'trust_score': trust.overall_score if trust else 50
        })
    
    # Calculate statistics for charts
    status_counts = {
        'pending': pending_bookings,
        'accepted': Booking.query.filter_by(status='accepted').count(),
        'completed': completed_bookings,
        'cancelled': Booking.query.filter_by(status='cancelled').count()
    }
    
    # Fraud risk distribution
    fraud_risk_counts = {
        'no_risk': FraudAlert.query.filter(FraudAlert.risk_score < 30).count(),
        'low': FraudAlert.query.filter(FraudAlert.risk_score.between(30, 50)).count(),
        'medium': FraudAlert.query.filter(FraudAlert.risk_score.between(50, 70)).count(),
        'high': FraudAlert.query.filter(FraudAlert.risk_score >= 70).count()
    }
    
    # Rating distribution
    rating_counts = {
        '5': Booking.query.filter_by(rating=5).count(),
        '4': Booking.query.filter_by(rating=4).count(),
        '3': Booking.query.filter_by(rating=3).count(),
        '2': Booking.query.filter_by(rating=2).count(),
        '1': Booking.query.filter_by(rating=1).count()
    }
    
    global_model = GlobalModel.query.filter_by(is_active=True).first()
    fl_stats = federated_orchestrator.get_stats()
    fraud_metrics = fraud_detector.get_metrics()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_plumbers=total_plumbers,
                         total_bookings=total_bookings,
                         completed_bookings=completed_bookings,
                         pending_bookings=pending_bookings,
                         fraud_alerts=fraud_alerts,
                         recent_bookings=recent_bookings,
                         all_reviews=all_reviews,
                         plumber_stats=plumber_stats,
                         customer_stats=customer_stats,
                         status_counts=status_counts,
                         fraud_risk_counts=fraud_risk_counts,
                         rating_counts=rating_counts,
                         global_model=global_model,
                         fl_stats=fl_stats,
                         fraud_metrics=fraud_metrics)

@app.route('/api/bookings/create', methods=['POST'])
@login_required
@role_required('customer')
def create_booking():
    data = request.get_json()
    
    plumber = Plumber.query.get(data.get('plumber_id'))
    if not plumber:
        return jsonify({'success': False, 'message': 'Plumber not found'}), 404
    
    booking = Booking(
        customer_id=current_user.id,
        plumber_id=plumber.id,
        service_description=data.get('service_description'),
        scheduled_date=datetime.fromisoformat(data.get('scheduled_date')),
        price=data.get('price')
    )
    
    db.session.add(booking)
    db.session.commit()
    
    booking_data = {
        'price': booking.price,
        'customer_total_bookings': Booking.query.filter_by(customer_id=current_user.id).count(),
        'plumber_total_bookings': Booking.query.filter_by(plumber_id=plumber.id).count(),
        'customer_cancellation_rate': 0.1,
        'plumber_cancellation_rate': 0.05,
        'time_to_booking_hours': 24,
        'price_deviation_from_avg': 0
    }
    
    fraud_result = fraud_detector.detect_anomaly(booking_data)
    
    if fraud_result['is_fraud'] and fraud_result['risk_score'] > 60:
        fraud_alert = FraudAlert(
            user_id=current_user.id,
            plumber_id=plumber.id,
            booking_id=booking.id,
            alert_type=fraud_result['fraud_type'],
            risk_score=fraud_result['risk_score'],
            description=fraud_result['description']
        )
        db.session.add(fraud_alert)
        db.session.commit()
    
    return jsonify({'success': True, 'booking_id': booking.id, 'fraud_check': fraud_result})

@app.route('/api/trust-score/<int:user_id>')
@login_required
def get_trust_score(user_id):
    trust_score = TrustScore.query.filter_by(user_id=user_id).first()
    
    if not trust_score:
        return jsonify({'error': 'Trust score not found'}), 404
    
    return jsonify({
        'overall_score': trust_score.overall_score,
        'completion_rate': trust_score.completion_rate,
        'review_authenticity': trust_score.review_authenticity,
        'response_time_score': trust_score.response_time_score,
        'anomaly_score': trust_score.anomaly_score,
        'total_transactions': trust_score.total_transactions
    })

@app.route('/api/federated/submit-update', methods=['POST'])
@login_required
def submit_federated_update():
    data = request.get_json()
    
    client_id = current_user.id
    local_weights = data.get('weights', [])
    num_samples = data.get('num_samples', 0)
    
    if not local_weights or num_samples == 0:
        return jsonify({'success': False, 'message': 'Invalid update data'}), 400
    
    federated_orchestrator.receive_local_update(client_id, local_weights, num_samples)
    
    local_update = LocalModelUpdate(
        user_id=current_user.id,
        model_version=federated_orchestrator.global_model_version,
        update_data=json.dumps(local_weights),
        data_samples_count=num_samples
    )
    db.session.add(local_update)
    db.session.commit()
    
    stats = federated_orchestrator.get_stats()
    
    return jsonify({
        'success': True,
        'message': 'Update received',
        'stats': stats
    })

@app.route('/api/federated/global-model')
@login_required
def get_global_model():
    global_model_data = federated_orchestrator.get_global_model()
    return jsonify(global_model_data)

@app.route('/api/federated/aggregate', methods=['POST'])
@login_required
@role_required('admin')
def aggregate_federated_updates():
    result = federated_orchestrator.aggregate_updates()
    
    if result['success']:
        global_model = GlobalModel(
            version=result['new_version'],
            model_data=json.dumps(federated_orchestrator.global_weights.tolist()),
            updates_aggregated=result['updates_aggregated']
        )
        db.session.add(global_model)
        db.session.commit()
    
    return jsonify(result)

@app.route('/api/fraud/detect', methods=['POST'])
@login_required
def detect_fraud():
    data = request.get_json()
    fraud_result = fraud_detector.detect_anomaly(data)
    return jsonify(fraud_result)

@app.route('/api/bookings/<int:booking_id>/accept', methods=['POST'])
@login_required
@role_required('plumber')
def accept_booking(booking_id):
    plumber = Plumber.query.filter_by(user_id=current_user.id).first()
    if not plumber:
        print(f"ERROR: Plumber profile not found for user_id={current_user.id}")
        return jsonify({'success': False, 'message': 'Plumber profile not found. Please contact admin.'}), 404
    
    booking = Booking.query.get(booking_id)
    if not booking:
        print(f"ERROR: Booking {booking_id} not found")
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    if booking.plumber_id != plumber.id:
        print(f"ERROR: Unauthorized - booking.plumber_id={booking.plumber_id}, plumber.id={plumber.id}")
        return jsonify({'success': False, 'message': 'This booking is not assigned to you'}), 403
    
    if booking.status != 'pending':
        print(f"ERROR: Booking status is {booking.status}, not pending")
        return jsonify({'success': False, 'message': f'Booking is already {booking.status}'}), 400
    
    booking.status = 'accepted'
    db.session.commit()
    print(f"SUCCESS: Booking {booking_id} accepted by plumber {plumber.id}")
    
    return jsonify({'success': True, 'message': 'Booking accepted successfully'})

@app.route('/api/bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
@role_required('plumber')
def reject_booking(booking_id):
    plumber = Plumber.query.filter_by(user_id=current_user.id).first()
    if not plumber:
        print(f"ERROR: Plumber profile not found for user_id={current_user.id}")
        return jsonify({'success': False, 'message': 'Plumber profile not found. Please contact admin.'}), 404
    
    booking = Booking.query.get(booking_id)
    if not booking:
        print(f"ERROR: Booking {booking_id} not found")
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    if booking.plumber_id != plumber.id:
        print(f"ERROR: Unauthorized - booking.plumber_id={booking.plumber_id}, plumber.id={plumber.id}")
        return jsonify({'success': False, 'message': 'This booking is not assigned to you'}), 403
    
    if booking.status not in ['pending', 'accepted']:
        print(f"ERROR: Booking status is {booking.status}, not pending or accepted")
        return jsonify({'success': False, 'message': f'Cannot reject booking with status: {booking.status}'}), 400
    
    # IMMEDIATE FRAUD DETECTION - Count all rejections by this plumber
    fraud_detected = False
    
    # Count total rejections/cancellations by this plumber (all time)
    total_rejections = Booking.query.filter(
        Booking.plumber_id == plumber.id,
        Booking.status == 'cancelled'
    ).count()
    
    # This rejection will be the (total_rejections + 1)th rejection
    # Flag fraud if this will be the 2nd or more rejection
    if total_rejections >= 1:  # After this rejection, it will be >= 2
        fraud_detected = True
        
        # Create fraud alert IMMEDIATELY
        fraud_alert = FraudAlert(
            user_id=current_user.id,
            plumber_id=plumber.id,
            booking_id=booking.id,
            alert_type='excessive_rejections',
            risk_score=70.0 + min(30, total_rejections * 10),  # Increases with more rejections
            description=f'Plumber has rejected {total_rejections + 1} bookings. Suspicious rejection pattern detected.',
            status='pending'
        )
        db.session.add(fraud_alert)
        
        # Reduce plumber trust score
        plumber_trust = TrustScore.query.filter_by(plumber_id=plumber.id).first()
        if plumber_trust:
            plumber_trust.anomaly_score = min(100, plumber_trust.anomaly_score + 15)
            plumber_trust.dispute_count += 1
            
            # Recalculate overall score
            metrics = {
                'completion_rate': plumber_trust.completion_rate / 100,
                'review_authenticity': plumber_trust.review_authenticity,
                'response_time_score': plumber_trust.response_time_score,
                'dispute_count': plumber_trust.dispute_count,
                'anomaly_score': plumber_trust.anomaly_score
            }
            updated_score = trust_scorer.calculate_trust_score(metrics)
            plumber_trust.overall_score = updated_score['overall_score']
            plumber_trust.updated_at = datetime.utcnow()
        
        print(f"FRAUD DETECTED: Plumber {plumber.id} has rejected {total_rejections + 1} bookings")
    
    booking.status = 'cancelled'
    db.session.commit()
    print(f"SUCCESS: Booking {booking_id} rejected by plumber {plumber.id}")
    
    message = 'Booking rejected successfully'
    if fraud_detected:
        message += f'. WARNING: You have rejected {total_rejections + 1} bookings. Excessive rejections have been flagged as suspicious. Admin has been notified.'
    
    return jsonify({
        'success': True, 
        'message': message,
        'fraud_warning': fraud_detected,
        'total_rejections': total_rejections + 1
    })

@app.route('/api/bookings/<int:booking_id>/complete', methods=['POST'])
@login_required
@role_required('plumber')
def complete_booking(booking_id):
    plumber = Plumber.query.filter_by(user_id=current_user.id).first()
    if not plumber:
        print(f"ERROR: Plumber profile not found for user_id={current_user.id}")
        return jsonify({'success': False, 'message': 'Plumber profile not found. Please contact admin.'}), 404
    
    booking = Booking.query.get(booking_id)
    if not booking:
        print(f"ERROR: Booking {booking_id} not found")
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    if booking.plumber_id != plumber.id:
        print(f"ERROR: Unauthorized - booking.plumber_id={booking.plumber_id}, plumber.id={plumber.id}")
        return jsonify({'success': False, 'message': 'This booking is not assigned to you'}), 403
    
    if booking.status != 'accepted':
        print(f"ERROR: Booking status is {booking.status}, not accepted")
        return jsonify({'success': False, 'message': f'Booking must be accepted first (current status: {booking.status})'}), 400
    
    booking.status = 'completed'
    booking.completed_at = datetime.utcnow()
    db.session.commit()
    print(f"SUCCESS: Booking {booking_id} completed by plumber {plumber.id}")
    
    return jsonify({'success': True, 'message': 'Booking marked as completed'})

def seed_database_if_empty():
    """Automatically seed database if it's empty (no users exist)"""
    with app.app_context():
        # Check if database is empty
        user_count = User.query.count()
        if user_count == 0:
            print("\n" + "="*60)
            print("DATABASE IS EMPTY - Running automatic seeding...")
            print("="*60 + "\n")
            
            # Create admin user
            print("Creating admin user...")
            admin = User(
                email='admin@gmail.com',
                password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'),
                name='Admin User',
                role='admin'
            )
            db.session.add(admin)
            
            # Create sample customers
            print("Creating sample customers...")
            customers = []
            for i in range(2):
                customer = User(
                    email=f'customer{i+1}@gmail.com',
                    password_hash=bcrypt.generate_password_hash('123456').decode('utf-8'),
                    name=f'Customer {i+1}',
                    role='customer'
                )
                db.session.add(customer)
                customers.append(customer)
                
                trust_score = TrustScore(
                    user=customer,
                    overall_score=random.uniform(40, 95),
                    completion_rate=random.uniform(0.5, 1.0) * 100,
                    review_authenticity=random.uniform(50, 100),
                    response_time_score=random.uniform(40, 100),
                    dispute_count=random.randint(0, 3),
                    anomaly_score=random.uniform(0, 30),
                    total_transactions=random.randint(1, 20)
                )
                db.session.add(trust_score)
            
            # Create sample plumbers
            print("Creating sample plumbers...")
            plumbers_data = [
                {'name': 'John Smith', 'specialty': 'Residential Plumbing', 'location': 'Bengaluru North', 'rate': 45, 'exp': 8},
                {'name': 'Sarah Johnson', 'specialty': 'Commercial Plumbing', 'location': 'Bengaluru South', 'rate': 60, 'exp': 12}
            ]
            
            plumbers = []
            for idx, data in enumerate(plumbers_data):
                user = User(
                    email=f'plumber{idx+1}@gmail.com',
                    password_hash=bcrypt.generate_password_hash('123456').decode('utf-8'),
                    name=data['name'],
                    role='plumber'
                )
                db.session.add(user)
                db.session.flush()
                
                plumber = Plumber(
                    user_id=user.id,
                    specialty=data['specialty'],
                    location=data['location'],
                    hourly_rate=data['rate'],
                    experience_years=data['exp'],
                    bio=f"Professional {data['specialty'].lower()} expert with {data['exp']} years of experience.",
                    available=True
                )
                db.session.add(plumber)
                db.session.flush()
                plumbers.append(plumber)
                
                trust_score = TrustScore(
                    plumber_id=plumber.id,
                    overall_score=random.uniform(60, 98),
                    completion_rate=random.uniform(0.75, 1.0) * 100,
                    review_authenticity=random.uniform(70, 100),
                    response_time_score=random.uniform(60, 100),
                    dispute_count=random.randint(0, 2),
                    anomaly_score=random.uniform(0, 20),
                    total_transactions=random.randint(5, 50)
                )
                db.session.add(trust_score)
            
            # Create sample bookings
            print("Creating sample bookings...")
            statuses = ['pending', 'accepted', 'completed', 'cancelled']
            for i in range(5):
                customer = random.choice(customers)
                plumber = random.choice(plumbers)
                
                booking = Booking(
                    customer_id=customer.id,
                    plumber_id=plumber.id,
                    service_description=f"Plumbing service request #{i+1}: {random.choice(['Leak repair', 'Pipe installation', 'Drain cleaning', 'Water heater repair', 'Bathroom renovation'])}",
                    scheduled_date=datetime.utcnow() + timedelta(days=random.randint(-10, 30)),
                    status=random.choice(statuses),
                    price=random.uniform(50, 300),
                    rating=random.randint(3, 5) if random.random() > 0.3 else None,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))
                )
                db.session.add(booking)
            
            # Create sample fraud alerts
            print("Creating sample fraud alerts...")
            fraud_types = ['price_manipulation', 'fake_booking', 'suspicious_pattern']
            for i in range(5):
                customer = random.choice(customers)
                plumber = random.choice(plumbers)
                
                alert = FraudAlert(
                    user_id=customer.id,
                    plumber_id=plumber.id,
                    alert_type=random.choice(fraud_types),
                    risk_score=random.uniform(40, 95),
                    description=f"Automated fraud detection flagged this transaction for {random.choice(['unusual pricing', 'high cancellation rate', 'suspicious booking pattern'])}",
                    status='pending',
                    flagged_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                )
                db.session.add(alert)
            
            # Create initial global model
            print("Creating initial global model...")
            global_model = GlobalModel(
                version=1,
                model_data='[0.1, -0.2, 0.3, -0.1, 0.4, -0.3, 0.2, -0.4, 0.1, 0.0]',
                accuracy=0.0,
                updates_aggregated=0,
                is_active=True
            )
            db.session.add(global_model)
            
            db.session.commit()
            print("\n" + "="*60)
            print("DATABASE SEEDED SUCCESSFULLY!")
            print("="*60)
            print("\nSample Credentials:")
            print("  Admin:    admin@gmail.com / admin")
            print("  Customer: customer1@gmail.com / 123456")
            print("  Plumber:  plumber1@gmail.com / 123456")
            print("="*60 + "\n")
        else:
            print(f"Database already contains {user_count} users. Skipping auto-seed.")

with app.app_context():
    db.create_all()
    federated_orchestrator.initialize_global_model()
    seed_database_if_empty()  # Auto-seed if empty



@app.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    # Allow both customers and plumbers to access this, but verify ownership
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    # Verify the user is the customer for this booking
    if booking.customer_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized - this is not your booking'}), 403
    
    if booking.status not in ['pending', 'accepted']:
        return jsonify({'success': False, 'message': f'Cannot cancel booking with status: {booking.status}'}), 400
    
    # Check if plumber already accepted - this is where we penalize
    penalty_applied = False
    credit_reduced = False

    # Count previous cancellations by this customer (before this one)
    previous_cancellations = Booking.query.filter_by(customer_id=current_user.id, status='cancelled').count()

    if booking.status == 'accepted':
        # Customer is cancelling after plumber accepted - reduce trust score
        customer_trust = TrustScore.query.filter_by(user_id=current_user.id).first()
        if customer_trust:
            # Increase anomaly score (bad behavior)
            customer_trust.anomaly_score = min(100, customer_trust.anomaly_score + 15)

            # Increase dispute count
            customer_trust.dispute_count += 1

            # Recalculate overall trust score
            metrics = {
                'completion_rate': customer_trust.completion_rate / 100,
                'review_authenticity': customer_trust.review_authenticity,
                'response_time_score': customer_trust.response_time_score,
                'dispute_count': customer_trust.dispute_count,
                'anomaly_score': customer_trust.anomaly_score
            }
            updated_score = trust_scorer.calculate_trust_score(metrics)
            customer_trust.overall_score = updated_score['overall_score']
            customer_trust.updated_at = datetime.utcnow()

            penalty_applied = True

    # If this cancellation will make the customer's total cancellations > 1, reduce credit a little
    # (counts all cancellations, regardless of whether plumber had accepted)
    if previous_cancellations + 1 > 1:
        customer_trust = TrustScore.query.filter_by(user_id=current_user.id).first()
        if customer_trust:
            # Reduce overall score slightly (small penalty)
            try:
                # Subtract a small amount (2 points) but keep within 0-100
                customer_trust.overall_score = max(0.0, customer_trust.overall_score - 2.0)
            except Exception:
                # Fallback in case overall_score is None or unexpected
                customer_trust.overall_score = max(0.0, (customer_trust.overall_score or 50.0) - 2.0)
            customer_trust.updated_at = datetime.utcnow()
            credit_reduced = True
    
    booking.status = 'cancelled'
    db.session.commit()
    
    message = 'Booking cancelled successfully'
    if penalty_applied:
        message += '. Note: Your trust score was reduced for cancelling after plumber acceptance.'
    if credit_reduced:
        message += ' Your credit (overall trust score) was slightly reduced because this is more than one cancellation.'

    # Prepare response details
    response = {
        'success': True,
        'message': message,
        'penalty_applied': penalty_applied,
        'credit_reduced': credit_reduced,
        'previous_cancellations': previous_cancellations
    }

    # Include new overall score if available
    if 'customer_trust' in locals() and customer_trust:
        response['new_overall_score'] = customer_trust.overall_score

    return jsonify(response)

@app.route('/api/bookings/<int:booking_id>/review', methods=['POST'])
@login_required
@role_required('customer')
def submit_review(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    if booking.customer_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if booking.status != 'completed':
        return jsonify({'success': False, 'message': 'Can only review completed bookings'}), 400
    
    if booking.rating:
        return jsonify({'success': False, 'message': 'Already reviewed'}), 400
    
    data = request.get_json()
    rating = data.get('rating')
    review = data.get('review')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Invalid rating'}), 400
    
    booking.rating = rating
    booking.review = review
    
    # Update plumber's trust score based on new review
    plumber_trust = TrustScore.query.filter_by(plumber_id=booking.plumber_id).first()
    if plumber_trust:
        plumber_trust.total_transactions += 1
        
        # Recalculate review authenticity
        all_reviews = Booking.query.filter_by(
            plumber_id=booking.plumber_id,
            status='completed'
        ).filter(Booking.rating.isnot(None)).all()
        
        reviews_data = [{'rating': b.rating, 'text': b.review or ''} for b in all_reviews]
        plumber_trust.review_authenticity = trust_scorer.estimate_review_authenticity(reviews_data)
        
        # Recalculate overall score
        metrics = {
            'completion_rate': plumber_trust.completion_rate / 100,
            'review_authenticity': plumber_trust.review_authenticity,
            'response_time_score': plumber_trust.response_time_score,
            'dispute_count': plumber_trust.dispute_count,
            'anomaly_score': plumber_trust.anomaly_score
        }
        updated_score = trust_scorer.calculate_trust_score(metrics)
        plumber_trust.overall_score = updated_score['overall_score']
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Review submitted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
