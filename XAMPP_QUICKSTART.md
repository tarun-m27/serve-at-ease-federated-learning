
# 🚀 XAMPP Quick Start Guide

## Prerequisites
✅ XAMPP installed  
✅ Python 3.8+ installed  
✅ Project files downloaded

---

## 5-Minute Setup

### Step 1: Start XAMPP Services
1. Open **XAMPP Control Panel**
2. Click **Start** for **Apache**
3. Click **Start** for **MySQL**
4. Wait for green status lights

### Step 2: Import Database
1. Open browser → `http://localhost/phpmyadmin`
2. Click **Import** tab
3. Choose file → `serve_at_ease_mysql.sql`
4. Click **Go**
5. ✅ Success message appears

### Step 3: Install Python Dependencies
Open terminal in project folder:
```bash
pip install -r requirements.txt
pip install pymysql
```

### Step 4: Configure Database Connection
Edit `config.py` - ensure this line is **UNCOMMENTED**:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/serve_at_ease'
```

And this line is **COMMENTED**:
```python
# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///serve_at_ease.db'
```

### Step 5: Run Application
```bash
python app.py
```

Open browser → `http://localhost:5000`

---

## 🔑 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@gmail.com | admin |
| **Customer** | customer1@example.com | password123 |
| **Plumber** | plumber1@example.com | password123 |

---

## ✅ Verify Setup

1. **Database Tables Created?**
   - Go to phpMyAdmin → `serve_at_ease` database
   - Should see 7 tables: users, plumbers, bookings, trust_scores, fraud_alerts, local_model_updates, global_models

2. **Sample Data Loaded?**
   - Click on `users` table → **Browse**
   - Should see admin + sample users

3. **Application Running?**
   - Browser shows landing page
   - Can login with credentials above

---

## 🔧 Troubleshooting

**Port 3306 already in use?**
- Stop other MySQL services
- Or change port in XAMPP config + `config.py`

**Can't connect to database?**
```bash
# Test connection:
mysql -u root -p
# Press Enter (no password by default)
```

**Import failed?**
- Ensure MySQL is running (green in XAMPP)
- Check file path is correct
- Try importing smaller sections

---

## 📊 Database Schema Overview

```
users (customers/plumbers/admin)
  ├── plumbers (service provider profiles)
  │     ├── bookings (service requests)
  │     └── trust_scores (plumber ratings)
  │
  ├── bookings (customer requests)
  │     ├── fraud_alerts (AI detection)
  │     └── reviews/ratings
  │
  └── trust_scores (customer reliability)

global_models (federated learning)
local_model_updates (ML training data)
```

---

## 🎯 Next Steps

1. ✅ Login as **admin@gmail.com**
2. ✅ Explore admin dashboard
3. ✅ Test customer booking flow
4. ✅ Test plumber acceptance flow
5. ✅ Submit reviews and ratings
6. ✅ Monitor fraud detection alerts

---

## 📝 SQL Queries Reference

### View all users:
```sql
SELECT * FROM users;
```

### View all bookings:
```sql
SELECT b.*, u.name AS customer_name, p.specialty 
FROM bookings b 
JOIN users u ON b.customer_id = u.id 
JOIN plumbers p ON b.plumber_id = p.id;
```

### View fraud alerts:
```sql
SELECT f.*, u.name AS customer_name, f.risk_score 
FROM fraud_alerts f 
JOIN users u ON f.user_id = u.id 
ORDER BY f.flagged_at DESC;
```

### View plumber ratings:
```sql
SELECT p.id, u.name, t.overall_score, t.total_transactions 
FROM plumbers p 
JOIN users u ON p.user_id = u.id 
JOIN trust_scores t ON t.plumber_id = p.id 
ORDER BY t.overall_score DESC;
```

### View completed bookings with reviews:
```sql
SELECT b.*, u.name AS customer, p.specialty AS plumber 
FROM bookings b 
JOIN users u ON b.customer_id = u.id 
JOIN plumbers pl ON b.plumber_id = pl.id 
JOIN users p ON pl.user_id = p.id 
WHERE b.status = 'completed' AND b.rating IS NOT NULL;
```

---

## 🛡️ Security Notes

- Change default passwords in production
- Set MySQL root password in XAMPP
- Enable SSL for production deployments
- Review fraud detection thresholds

---

**Need Help?** Check `XAMPP_SETUP.md` for detailed instructions!
