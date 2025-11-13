# Serve at Ease

## AI-Driven Federated Learning and Trust Scoring Framework for Service Platforms

A privacy-first plumber booking platform that revolutionizes service marketplaces by integrating federated learning with transparent trust-scoring to mitigate data exposure, bias, and fraud while maintaining scalability.

---

## Overview

**Serve at Ease** demonstrates the practical application of cutting-edge research in federated learning and AI-powered fraud detection for real-world service platforms. Unlike centralized analytics that aggregate raw user and vendor data, our system coordinates decentralized model training on edge nodes and exchanges only anonymized model updates for aggregation.

### Key Innovations

1. **Federated Learning**: Privacy-preserving AI where models train locally on user devices, sharing only encrypted gradients
2. **AI-Powered Fraud Detection**: Real-time anomaly detection using machine learning to identify fake bookings and price manipulation
3. **Multi-Factor Trust Scoring**: Transparent reputation system based on completion rates, review authenticity, and behavioral patterns

---

## Features

### For Customers
- **Search & Book Plumbers**: Browse available plumbers by specialty, location, and ratings
- **View Trust Scores**: See transparent trust metrics for all service providers
- **Track Bookings**: Monitor booking status from request to completion
- **Leave Reviews**: Rate and review completed services

### For Plumbers
- **Manage Services**: Create and update service offerings
- **Accept Bookings**: Review and respond to customer requests
- **Build Reputation**: Track performance metrics and trust score
- **Federated Learning Participation**: Contribute to platform-wide fraud detection while keeping data private

### For Admins
- **Fraud Detection Dashboard**: Monitor real-time fraud alerts and risk patterns
- **Federated Learning Control**: Manage global model aggregation and updates
- **Platform Analytics**: View comprehensive statistics and trends
- **User Management**: Oversee all users, plumbers, and bookings

---

## Technology Stack

### Backend
- **Python Flask**: Web framework
- **PostgreSQL**: SQL database via SQLAlchemy ORM
- **Flask-Login**: Session management and authentication
- **Flask-Bcrypt**: Password hashing

### AI/Machine Learning
- **Scikit-learn**: Fraud detection models
- **Isolation Forest**: Anomaly detection algorithm. It works by isolating "outliers" within the data. In the context of fraud detection, this means identifying booking patterns that deviate significantly from normal behavior, such as unusually frequent cancellations, price anomalies, or rapid booking times.
- **NumPy & Pandas**: Data processing
- **Custom FedAvg Implementation**: Federated learning orchestrator

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Interactive data visualizations
- **Jinja2**: Template engine

---

## System Architecture

```
User/Plumber Device → Local Model Training (Private Data)
                    ↓
            Encrypted Model Updates
                    ↓
        Federated Orchestrator (Server)
                    ↓
            Global Model Aggregation
                    ↓
        Updated Global Model Distribution
                    ↓
    Trust Score & Fraud Detection Updates
```

### Database Schema

- **Users**: Authentication and role management (customer, plumber, admin)
- **Plumbers**: Service provider profiles with specialty and pricing
- **Bookings**: Service requests with status tracking
- **TrustScores**: Multi-factor trust metrics for users and plumbers
- **FraudAlerts**: AI-detected suspicious activities
- **LocalModelUpdates**: Federated learning update tracking
- **GlobalModel**: Aggregated federated learning models with versioning

---

## Getting Started

### Option 1: Run on Replit (PostgreSQL)

1. Click the **Run** button
2. Database is automatically configured
3. Access at the provided Replit URL

### Option 2: Run Locally with XAMPP (MySQL)

**🚀 Quick Start:** See [XAMPP_QUICKSTART.md](XAMPP_QUICKSTART.md) for 5-minute setup!

1. **Install XAMPP** from [apachefriends.org](https://www.apachefriends.org/)

2. **Start MySQL** in XAMPP Control Panel

3. **Import database** in phpMyAdmin:
   - Click **Import** → Choose `serve_at_ease_mysql.sql` → Click **Go**
   - OR manually create database: `serve_at_ease`

4. **Configure database** in `config.py`:
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/serve_at_ease'
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pymysql
   ```

6. **Run application**
   ```bash
   python app.py
   ```

7. **Access** at `http://localhost:5000`

📖 **Detailed guides:**
- [XAMPP_QUICKSTART.md](XAMPP_QUICKSTART.md) - Fast 5-minute setup
- [XAMPP_SETUP.md](XAMPP_SETUP.md) - Complete instructions with troubleshooting

---

## Sample Credentials

After seeding the database:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@gmail.com | admin |
| Customer | customer1@example.com | password123 |
| Plumber | plumber1@example.com | password123 |

---

## API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - User login
- `GET /logout` - User logout

### Bookings
- `POST /api/bookings/create` - Create booking with fraud check
- View bookings via role-specific dashboards

### Trust Scoring
- `GET /api/trust-score/<user_id>` - Retrieve trust score details

### Federated Learning
- `POST /api/federated/submit-update` - Submit local model update
- `GET /api/federated/global-model` - Retrieve global model
- `POST /api/federated/aggregate` - Trigger aggregation (admin only)

### Fraud Detection
- `POST /api/fraud/detect` - Analyze booking for fraud patterns

---

## Federated Learning Implementation

### FedAvg Algorithm

Our implementation uses Federated Averaging (McMahan et al., 2017):

1. **Local Training**: Each client (user/plumber) trains a model on their private data
2. **Update Submission**: Clients send only model weights/gradients, not raw data
3. **Weighted Aggregation**: Server aggregates updates based on sample counts
4. **Global Distribution**: Updated global model is distributed to all clients

### Privacy Preservation

- **Data Locality**: User data never leaves their device
- **Encrypted Updates**: Model updates are transmitted securely
- **No Raw Data Sharing**: Only aggregated model parameters are stored

---

## Fraud Detection System

### Detection Types

1. **Price Manipulation**: Abnormal pricing compared to market averages
2. **Fake Bookings**: High cancellation rates indicating fraudulent behavior
3. **Rush Booking Scams**: Extremely short booking notice times
4. **Suspicious Patterns**: General anomalous behavior detected by ML

### Risk Scoring

- **0-30**: Low risk (normal transaction)
- **30-60**: Medium risk (flagged for review)
- **60-100**: High risk (immediate fraud alert)

**How it works:** When a new user is created or a new booking is made, the system analyzes the transaction against historical patterns and known fraudulent behaviors. The **Isolation Forest** model, trained on anonymized data, identifies deviations from normal activity. For new users, it looks for patterns like immediate high-value bookings or unusual account creation details. For new bookings, it assesses factors like price, timing, and user history. If a transaction falls outside normal parameters, it's flagged with a risk score, potentially triggering an alert.

---

## Code & Methodology (fraud detection, trust adjustments, federated flow)

This section maps the implemented methods and endpoints to the code so developers can quickly find and extend the core functionality.

- Fraud detection engine
   - File: `ml_models/fraud_detector.py`
   - Key class: `FraudDetector` (module-level instance `fraud_detector`)
   - Main methods:
      - `extract_features(booking_data)`: turns booking attributes (price, cancellation rates, time-to-booking, etc.) into feature vectors.
      - `detect_anomaly(booking_data)`: returns `{ is_fraud, risk_score, fraud_type, description }` using an Isolation Forest.
      - `train(training_data, true_labels)`, `save_model(path)`, `load_model(path)`: utilities for model lifecycle management.

- Where fraud detection is called
   - Booking creation endpoint: `app.py` -> `POST /api/bookings/create` constructs `booking_data` and calls `fraud_detector.detect_anomaly(booking_data)`; a `FraudAlert` is persisted when risk is high.
   - Manual check endpoint: `POST /api/fraud/detect` forwards arbitrary booking data to `fraud_detector.detect_anomaly` for on-demand analysis.

- Trust / credit adjustments (where scores are reduced)
   - File: `app.py`
   - Customer cancels after plumber accepted: `POST /api/bookings/<booking_id>/cancel` updates the customer's `TrustScore` (fields like `anomaly_score`, `dispute_count`) and recalculates `overall_score` via `ml_models/trust_scorer.py`.
   - Repeated cancellations: the cancel handler now counts prior cancellations and applies a small additional penalty (prototype: -2 overall score points when total cancellations > 1). See `app.py` cancel handler for the exact implementation and the returned `credit_reduced` flag in the JSON response.
   - Plumber excessive rejections: `POST /api/bookings/<booking_id>/reject` counts previous cancellations/rejections and creates `FraudAlert` and updates plumber `TrustScore` (increasing `anomaly_score` and recalculating `overall_score`).

- Federated learning (where and how)
   - Core orchestrator: `ml_models/federated_orchestrator.py` (class `FederatedOrchestrator`, instance `federated_orchestrator`)
      - `receive_local_update(client_id, local_weights, num_samples)`: enqueue local updates
      - `aggregate_updates()`: FedAvg weighted by `num_samples` (configurable `min_updates_for_aggregation`)
      - `get_global_model()`: returns current weights and version
      - `simulate_local_training(...)`: helper for producing demo updates
   - API wiring (in `app.py`):
      - `POST /api/federated/submit-update` — clients submit local model updates; server stores `LocalModelUpdate` and calls `receive_local_update`.
      - `GET /api/federated/global-model` — clients download latest global weights and version.
      - `POST /api/federated/aggregate` — admin-only endpoint to trigger `aggregate_updates()` and persist a `GlobalModel` record.

- Data persistence and auditability
   - Tables: `LocalModelUpdate` and `GlobalModel` in `models/database.py` record client submissions and aggregated artifacts for auditing and debugging.

- Practical recommendations for production
   - Add secure aggregation so the server cannot observe individual updates.
   - Add differential privacy mechanisms to limit information leakage from model weights.
   - Authenticate and rate-limit federated endpoints to prevent spoofing and abuse.

---


---

## Trust Scoring System

### Factors (Weighted)

1. **Completion Rate (30%)**: Percentage of bookings completed successfully
2. **Review Authenticity (25%)**: Quality and genuineness of reviews
3. **Response Time (20%)**: Speed of responding to booking requests
4. **Dispute History (15%)**: Penalty for disputes and cancellations
5. **Anomaly Score (10%)**: Penalty for suspicious behavior patterns

### Trust Levels

- **80-100**: Excellent (Highly trusted)
- **60-79**: Good (Reliable)
- **40-59**: Fair (Average)
- **20-39**: Poor (Concerning)
- **0-19**: Very Low (High risk)

---

## Project Structure

```
serve-at-ease/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── seed_data.py                   # Database seeding script
├── models/
│   └── database.py                # SQLAlchemy ORM models
├── ml_models/
│   ├── fraud_detector.py          # Fraud detection engine
│   ├── federated_orchestrator.py  # Federated learning coordinator
│   └── trust_scorer.py            # Trust scoring calculator
├── templates/
│   ├── base.html                  # Base template
│   ├── landing.html               # Landing page
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── customer_dashboard.html    # Customer dashboard
│   ├── plumber_dashboard.html     # Plumber dashboard
│   └── admin_dashboard.html       # Admin control panel
└── static/
    ├── css/
    │   └── style.css             # Custom styles
    └── js/                       # JavaScript files
```

---

## Future Enhancements

As outlined in the research paper, potential improvements include:

1. **Production Federated Learning**: Deploy TensorFlow Federated or PySyft
2. **Differential Privacy**: Add calibrated noise to protect individual updates
3. **Blockchain Integration**: Implement blockchain-backed update attestation
4. **Robust Aggregation**: Deploy Byzantine-tolerant aggregation (Krum, Trimmed Mean)
5. **Advanced Fraud Models**: LSTM for sequential patterns, Graph Neural Networks
6. **Real-time Notifications**: Email/SMS alerts for fraud events
7. **A/B Testing Framework**: Evaluate trust scoring algorithms

---

## Research Foundation

This implementation is based on the research paper:

**"Serve at Ease: An AI-Driven Federated Learning and Trust Scoring Framework for Service Platforms"**

*Authors: Tarun M, Vinayaka V M, Swayam Sidnale, Vivek Gunari*

*Department of Computer Science and Engineering, Dayananda Sagar College of Engineering, Bengaluru, Karnataka, India*

### Key References
- McMahan et al. (2017): Communication-Efficient Learning of Deep Networks from Decentralized Data
- Kairouz et al. (2021): Advances and Open Problems in Federated Learning
- Bonawitz et al. (2019): Towards Federated Learning at Scale

---

## Security Considerations

- **Password Hashing**: Bcrypt with salt for secure password storage
- **Session Management**: Flask-Login for secure session handling
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **CSRF Protection**: Built-in Flask protections
- **Environment Variables**: Sensitive credentials stored in environment

---

## Contributing

This is a research prototype demonstrating federated learning and fraud detection concepts. Contributions are welcome for:
- Enhanced ML models
- Additional fraud detection patterns
- UI/UX improvements
- Performance optimizations

---

## License

This project is developed as part of academic research at Dayananda Sagar College of Engineering.

---

## Contact

For questions or collaboration opportunities, please contact the authors through the Department of Computer Science and Engineering, Dayananda Sagar College of Engineering, Bengaluru.

---

**Serve at Ease** - Revolutionizing service platforms through privacy-preserving AI and transparent trust scoring.