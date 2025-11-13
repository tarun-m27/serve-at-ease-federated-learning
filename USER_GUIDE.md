# Serve at Ease - User Guide

## Quick Start Guide

### Accessing the Platform

Your application is now running at: **http://localhost:5000**

---

## Sample Accounts

The database has been pre-populated with sample data. You can login with these credentials:

### Admin Account
- **Email**: admin@serveatease.com
- **Password**: admin123
- **Features**: Access to fraud detection dashboard, federated learning controls, and platform analytics

### Customer Account
- **Email**: customer1@example.com
- **Password**: password123
- **Features**: Search plumbers, book services, view trust scores

### Plumber Account
- **Email**: plumber1@example.com
- **Password**: password123
- **Features**: Manage services, accept bookings, participate in federated learning

---

## Using the Platform

### As a Customer

1. **Register/Login**
   - Navigate to the registration page
   - Choose "Customer" role
   - Fill in your details

2. **Search for Plumbers**
   - Browse available plumbers on your dashboard
   - View their specialties, locations, hourly rates, and experience
   - Check their trust scores

3. **Book a Service**
   - Click "Book Service" on a plumber's card
   - Enter service description (e.g., "Fix kitchen sink leak")
   - Specify price and scheduled date
   - The system automatically runs fraud detection on your booking

4. **Track Bookings**
   - View all your bookings in the dashboard
   - Monitor status: pending, accepted, completed, cancelled
   - Leave reviews after service completion

5. **View Your Trust Score**
   - See your overall trust rating
   - Check detailed metrics: completion rate, review authenticity, response time

---

### As a Plumber

1. **Register/Login**
   - Choose "Plumber" role during registration
   - Provide specialty, location, hourly rate, and experience

2. **Manage Profile**
   - Update your specialty and availability
   - Set competitive hourly rates
   - Build your bio

3. **Handle Bookings**
   - View incoming booking requests
   - Accept or reject bookings
   - Mark completed bookings as done

4. **Build Reputation**
   - Track your trust score
   - Monitor performance metrics
   - Improve completion rates and response times

5. **Participate in Federated Learning**
   - Click "Simulate Model Update Submission" to contribute to platform-wide fraud detection
   - Your data stays private - only encrypted model updates are shared

---

### As an Admin

1. **Login with Admin Credentials**
   - Email: admin@serveatease.com
   - Password: admin123

2. **Monitor Platform Statistics**
   - View total users, plumbers, and bookings
   - Track platform growth

3. **Review Fraud Alerts**
   - See real-time fraud detection alerts
   - Review suspicious bookings flagged by AI
   - Check risk scores and fraud types

4. **Manage Federated Learning**
   - View global model version and status
   - See pending model updates from users
   - Trigger model aggregation when enough updates are collected
   - Monitor model accuracy and performance

5. **Analyze Platform Data**
   - View booking trends with Chart.js visualizations
   - Analyze fraud risk distribution
   - Review recent bookings across the platform

---

## Understanding the Features

### Federated Learning Explained

**What is it?**
- A privacy-preserving way to train AI models
- Your data stays on your device
- Only encrypted model updates are shared with the server

**How it works:**
1. Your device trains a small model on your private booking/review data
2. The model learns patterns of legitimate vs fraudulent behavior
3. Only the learned model weights (not your data) are sent to the server
4. The server combines updates from many users to improve the global model
5. The improved model is sent back to help detect fraud more accurately

**Benefits:**
- Privacy: Your raw data never leaves your device
- Security: No central database vulnerability
- Accuracy: Learning from thousands of users improves detection

---

### Fraud Detection System

**What gets detected:**
- **Price Manipulation**: Abnormal pricing far from market averages
- **Fake Bookings**: Patterns of frequent cancellations
- **Rush Scams**: Extremely short booking notice suggesting urgency scams
- **Suspicious Patterns**: Unusual booking behavior

**Risk Levels:**
- 🟢 **Low (0-30)**: Normal transaction
- 🟡 **Medium (30-60)**: Flagged for review
- 🔴 **High (60-100)**: Immediate fraud alert

**When bookings are checked:**
- Automatically when a customer creates a booking
- Risk score is calculated in real-time
- High-risk bookings trigger fraud alerts for admin review

---

### Trust Score System

Your trust score is calculated from multiple factors:

1. **Completion Rate (30% weight)**
   - Percentage of bookings you complete successfully
   - Higher is better

2. **Review Authenticity (25% weight)**
   - Quality and genuineness of reviews you receive/give
   - Varied ratings with detailed reviews score higher

3. **Response Time (20% weight)**
   - How quickly you respond to bookings/messages
   - Faster responses = higher score

4. **Dispute History (15% weight)**
   - Number of disputes or complaints
   - Fewer disputes = higher score

5. **Anomaly Score (10% weight)**
   - Unusual behavior patterns detected by AI
   - Lower anomaly = higher trust

**Trust Levels:**
- 🌟 **Excellent (80-100)**: Highly trusted user
- ✅ **Good (60-79)**: Reliable user
- ⚠️ **Fair (40-59)**: Average user
- ❌ **Poor (20-39)**: Concerning behavior
- 🚫 **Very Low (0-19)**: High risk user

---

## API Testing

You can test the API endpoints using tools like Postman or curl:

### Example: Get Trust Score
```bash
curl http://localhost:5000/api/trust-score/1
```

### Example: Submit Federated Update
```bash
curl -X POST http://localhost:5000/api/federated/submit-update \
  -H "Content-Type: application/json" \
  -d '{"weights": [0.1, -0.2, 0.3], "num_samples": 50}'
```

### Example: Detect Fraud
```bash
curl -X POST http://localhost:5000/api/fraud/detect \
  -H "Content-Type: application/json" \
  -d '{"price": 500, "customer_total_bookings": 2, "price_deviation_from_avg": 3}'
```

---

## Troubleshooting

### Can't Login?
- Ensure you're using the correct email and password
- Try one of the sample accounts listed above

### Booking Not Working?
- Make sure you're logged in as a customer
- Check that the plumber is available
- Verify all required fields are filled

### Fraud Alert Appeared?
- This is normal for testing - the system is working
- In production, genuine bookings rarely trigger alerts
- Admins can review and clear false positives

### Trust Score Not Updating?
- Trust scores update after bookings are completed
- New users start with baseline scores
- Participate in more transactions to see changes

---

## Tips for Demo/Testing

1. **Test Multiple Roles**
   - Login as customer, plumber, and admin
   - See how each dashboard differs

2. **Create Bookings**
   - Make several bookings to see the system in action
   - Try different price points to trigger fraud detection

3. **Submit Federated Updates**
   - As a plumber, simulate model updates
   - Watch the admin dashboard update pending counts

4. **Trigger Aggregation**
   - As admin, once you have 3+ updates, trigger aggregation
   - See the global model version increment

5. **Explore Visualizations**
   - Check the Chart.js graphs on admin dashboard
   - View trust score breakdowns on customer/plumber dashboards

---

## Next Steps

### For Development
- Train the fraud detection model with real data
- Integrate actual TensorFlow Federated for production FL
- Add email notifications for fraud alerts
- Implement payment processing
- Add real-time chat between customers and plumbers

### For Deployment
- Configure production database settings
- Set up proper environment variables
- Use a production WSGI server (Gunicorn)
- Enable HTTPS/SSL
- Set up monitoring and logging

---

## Support

For questions about the implementation or research paper, refer to:
- **README.md**: Complete technical documentation
- **Research Paper**: "Serve at Ease" research document
- **Code Comments**: Inline documentation in source files

---

**Happy Testing!** 🚀
