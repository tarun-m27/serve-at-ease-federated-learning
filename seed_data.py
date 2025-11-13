from app import app, db, bcrypt
from models.database import User, Plumber, Booking, TrustScore, FraudAlert, GlobalModel
from datetime import datetime, timedelta
import random

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Creating admin user...")
        admin = User(
        email='admin@gmail.com',
        password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'),
        name='Admin User',
        role='admin'
    )
        db.session.add(admin)

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
        print("Database seeded successfully!")
        print("\nSample Credentials:")
        print("Admin: admin@gmail.com / admin")
        print("Customer: customer1@gmail.com / 123456")
        print("Plumber: plumber1@gmail.com / 123456")

if __name__ == '__main__':
    seed_database()