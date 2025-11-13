
# XAMPP Setup Guide for Serve at Ease

## Prerequisites
- XAMPP installed on your Windows/Mac/Linux system
- Python 3.8+ installed

---

## Step 1: Install XAMPP

1. Download XAMPP from [https://www.apachefriends.org/](https://www.apachefriends.org/)
2. Install XAMPP (default installation path: `C:\xampp` on Windows)
3. Start XAMPP Control Panel

---

## Step 2: Start MySQL Server

1. Open XAMPP Control Panel
2. Click **Start** next to **MySQL**
3. Wait for MySQL to start (green highlight)
4. Click **Admin** next to MySQL to open phpMyAdmin

---

## Step 3: Import Database

### Option A: Import SQL File (Recommended)

1. In phpMyAdmin, click **Import** tab
2. Click **Choose File** and select `serve_at_ease_mysql.sql` from your project
3. Click **Go** at the bottom
4. Wait for import to complete ✓

### Option B: Create Empty Database

1. In phpMyAdmin, click **New** (left sidebar)
2. Enter database name: `serve_at_ease`
3. Choose collation: `utf8mb4_general_ci`
4. Click **Create**
5. Then run `python seed_data.py` to populate data

---

## Step 4: Configure Application

Edit `config.py` in your project root:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # XAMPP MySQL Configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/serve_at_ease'
    
    # If you set a MySQL root password in XAMPP:
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/serve_at_ease'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
```

---

## Step 5: Install MySQL Python Connector

Open Command Prompt/Terminal and run:

```bash
pip install pymysql
```

**Note:** The `serve_at_ease_mysql.sql` file contains:
- Complete database schema with all tables
- Foreign key constraints for data integrity
- Sample data (admin, customers, plumbers, trust scores)
- Default credentials for testing

---

## Step 6: Initialize Database

Run these commands in your project directory:

```bash
# Seed the database with sample data
python seed_data.py
```

---

## Step 7: Run the Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

---

## Default XAMPP MySQL Settings

- **Host:** localhost
- **Port:** 3306
- **Username:** root
- **Password:** (empty by default)
- **Database:** serve_at_ease

---

## Troubleshooting

### Error: "Access denied for user 'root'@'localhost'"

**Solution:** You may have set a password for MySQL root user.

1. Open XAMPP Control Panel
2. Click **Shell** button
3. Run: `mysql -u root -p`
4. Enter your password
5. Run: `ALTER USER 'root'@'localhost' IDENTIFIED BY '';` (to remove password)

OR update `config.py` with your password:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/serve_at_ease'
```

---

### Error: "MySQL module not found"

**Solution:** Install PyMySQL:
```bash
pip install pymysql
```

---

### Error: "Can't connect to MySQL server"

**Solution:** 
1. Ensure MySQL is running in XAMPP Control Panel (green status)
2. Check if port 3306 is not blocked by firewall
3. Try restarting MySQL in XAMPP

---

### Error: "Unknown database 'serve_at_ease'"

**Solution:** Create the database manually:
1. Open phpMyAdmin (http://localhost/phpmyadmin)
2. Click **New** 
3. Database name: `serve_at_ease`
4. Click **Create**

---

## How Fraud Detection Works

### Detection Triggers

Fraud detection runs **automatically** when:

1. **A customer creates a new booking** → System analyzes in real-time
2. **A booking is modified** → Re-evaluates fraud risk
3. **Suspicious patterns detected** → Generates fraud alert

### Fraud Detection Factors

The AI model analyzes **7 key features**:

1. **Price** - Is it unusually high/low?
2. **Customer booking count** - New users are higher risk
3. **Plumber booking count** - New plumbers are higher risk
4. **Customer cancellation rate** - Frequent cancellations = red flag
5. **Plumber cancellation rate** - Provider reliability
6. **Time to booking** - Rush bookings (< 1 hour) are suspicious
7. **Price deviation** - How far from average market price?

### Fraud Types Detected

- **Price Manipulation** - Price 2x+ above average
- **Fake Bookings** - High cancellation rate (> 50%)
- **Rush Scams** - Booking within 1 hour (urgency tactic)
- **Suspicious Patterns** - Anomalous behavior detected by ML

### Risk Scoring

- **0-30%** → Low Risk (Green) - Normal transaction
- **30-60%** → Medium Risk (Yellow) - Flagged for review
- **60-100%** → High Risk (Red) - Fraud alert generated

### Example: Creating Fraud Alerts

When you create a **new user** and they make bookings:

**Scenario 1: Normal User**
```
Price: $100 (average market price)
Customer bookings: 5
Cancellation rate: 10%
Time to booking: 24 hours
→ Risk Score: 15% (Low Risk) ✓
```

**Scenario 2: Fraudulent User**
```
Price: $500 (5x above average!)
Customer bookings: 1 (new user)
Cancellation rate: 80% (suspicious!)
Time to booking: 0.5 hours (rush!)
→ Risk Score: 92% (High Risk) ⚠️
→ FRAUD ALERT GENERATED
```

### Testing Fraud Detection

To generate fraud alerts:

1. Create a new customer account
2. Book a service with **very high price** (e.g., $999)
3. Book with **very short notice** (schedule within 1 hour)
4. Admin dashboard will show the fraud alert

---

## Production Deployment Notes

For production on your laptop:

1. **Set a strong SECRET_KEY** in `config.py`
2. **Set MySQL root password** in XAMPP
3. **Disable debug mode** in `app.py`:
   ```python
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=False)
   ```
4. **Use production WSGI server** (Waitress for Windows):
   ```bash
   pip install waitress
   ```
   
   Create `run_production.py`:
   ```python
   from waitress import serve
   from app import app
   
   serve(app, host='0.0.0.0', port=5000)
   ```

---

## Sample Credentials

After running `seed_data.py`:

- **Admin:** admin@gmail.com / admin
- **Customer:** customer1@example.com / password123
- **Plumber:** plumber1@example.com / password123
