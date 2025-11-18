# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands & workflows

### Environment & dependencies

- Python version: see `runtime.txt` (currently `3.11.10`).
- Install core dependencies:
  - `pip install -r requirements.txt`
- For **MySQL mode** only (optional):
  - `pip install pymysql`

### Running the application (development)

The app is a single Flask service rooted at `app.py`. Configuration is provided by `config.Config`.

**Default (SQLite, no external DB required)**

If `DATABASE_URL` is **not** set and `USE_MYSQL != '1'`, the app uses a SQLite file `serve_at_ease.db` in the repo directory.

From the project root:

```bash
python app.py
```

On first run with an empty database, startup logic in `app.py` will:
- Call `db.create_all()` to create tables from `models/database.py`.
- Initialize the federated global model via `federated_orchestrator.initialize_global_model()`.
- Auto-seed sample data via `seed_database_if_empty()` (admin, customers, plumbers, bookings, fraud alerts, initial `GlobalModel`).

### Database configuration modes

All DB selection happens in `config.Config`:

1. **PostgreSQL (production-style)**
   - If `DATABASE_URL` is set, it is used as `SQLALCHEMY_DATABASE_URI`.
   - The code automatically normalizes `postgres://` -> `postgresql://` for SQLAlchemy.
   - This is how the Render deployment is wired (see `render.yaml`).

2. **MySQL (XAMPP-style local setup)**
   - Enable by setting `USE_MYSQL=1` in the environment.
   - Optional overrides (all via env vars):
     - `MYSQL_HOST` (default `localhost`)
     - `MYSQL_PORT` (default `3306`)
     - `MYSQL_USER` (default `root`)
     - `MYSQL_PASSWORD` (default empty)
     - `MYSQL_DATABASE` (default `serve_at_ease`)
   - `Config` builds `SQLALCHEMY_DATABASE_URI` as
     `mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}`.
   - Older README snippets still show a hard-coded URI in `config.py`; prefer the env-driven approach above when updating code.

3. **SQLite (default)**
   - When neither `DATABASE_URL` nor `USE_MYSQL=1` is set, `SQLALCHEMY_DATABASE_URI` points at the local `serve_at_ease.db` file.

### Seeding and resetting the database

There are two seeding flows:

- **On normal app startup** (`python app.py`):
  - `with app.app_context(): db.create_all(); seed_database_if_empty()` runs at import time.
  - If there are **no users**, it seeds admin, sample customers/plumbers, bookings, fraud alerts, and a `GlobalModel`.
  - If users already exist, auto-seeding is skipped.

- **Explicit reseed (destructive)**:
  - `python seed_data.py`
  - This script:
    - Drops **all** tables (`db.drop_all()`), recreates them, and then seeds admin, customers, plumbers, bookings, fraud alerts, and a `GlobalModel`.
  - Use this when you need a clean demo dataset; be aware it erases existing data in the current database.

### Running in a production-like way (Render)

`render.yaml` configures the hosted service with:

- Build step:
  - `pip install -r requirements.txt`
- Start command:
  - `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app`

You can reuse this locally if you want to mirror Render’s process model (ensure `gunicorn` is installed and `PORT` is set), but for normal development `python app.py` is sufficient.

### Testing & linting

- There is **no dedicated test suite or test runner configuration** (no `tests/` package, no CI config, no linting tools like `flake8`/`black` in `requirements.txt`).
- If you introduce tests, a typical pattern is to use `pytest` and run either:
  - `pytest` (all tests), or
  - `pytest path/to/test_file.py::TestClass::test_case` (single test).
- When adding tooling, keep commands in line with the existing Python/Flask stack and document them in `README.md` and/or here.

### Useful API smoke checks

The user guide (`USER_GUIDE.md`) includes curl examples; they are useful for quick manual verification of core flows:

- Get trust score:
  - `curl http://localhost:5000/api/trust-score/1`
- Submit a federated update:
  - `curl -X POST http://localhost:5000/api/federated/submit-update -H "Content-Type: application/json" -d '{"weights": [0.1, -0.2, 0.3], "num_samples": 50}'`
- Run a fraud detection check:
  - `curl -X POST http://localhost:5000/api/fraud/detect -H "Content-Type: application/json" -d '{"price": 500, "customer_total_bookings": 2, "price_deviation_from_avg": 3}'`

These endpoints require an authenticated session when called via the browser; when hitting them via HTTP clients, wire in authentication as needed if that behavior is changed.


## High-level architecture

### Overall structure

The project is a monolithic Flask application implementing a three-sided marketplace (customers, plumbers, admin) with integrated fraud detection, trust scoring, and a toy federated learning pipeline.

Key modules (see also the "Project Structure" section in `README.md`):

- `app.py` – Flask app factory and all routes (HTML pages + JSON APIs), role-based dashboards, booking lifecycle, fraud detection and trust adjustments, federated endpoints, and auto-seeding at startup.
- `config.py` – `Config` class that encapsulates database selection (PostgreSQL, MySQL, SQLite) and general app settings.
- `models/database.py` – SQLAlchemy models and `db` handle:
  - `User` (`UserMixin`) with role (`customer`, `plumber`, `admin`).
  - `Plumber` profile linked 1:1 to a `User` with plumber role.
  - `Booking` linking customers and plumbers, including status, price, rating, and timestamps.
  - `TrustScore` attached either to a `User` (customer trust) or `Plumber` (plumber trust).
  - `FraudAlert` for AI and rule-generated alerts.
  - `LocalModelUpdate` and `GlobalModel` for federated learning audit trail.
- `ml_models/` – ML and scoring components exposed as singletons imported into `app.py`:
  - `fraud_detector.py` → `fraud_detector` (Isolation Forest + rule-based fallback).
  - `federated_orchestrator.py` → `federated_orchestrator` (FedAvg with simple in-memory update queue).
  - `trust_scorer.py` → `trust_scorer` (weighted trust computation and helper metrics).
- `templates/` – Jinja2 templates for landing page, auth flows, and dashboards per role.
- `static/` – Bootstrap-based CSS, JS, and assets.

### Request and role flow

- Landing and auth:
  - `/` → `landing.html` marketing/overview page.
  - `/register`, `/login`, `/logout` handle account lifecycle via `Flask-Login` and `Flask-Bcrypt`.
  - After login, `/dashboard` redirects based on `current_user.role` to the appropriate dashboard.

- Dashboards (HTML):
  - **Customer** (`/customer/dashboard`): lists the user’s bookings, trust score, and available plumbers; drives booking creation from UI.
  - **Plumber** (`/plumber/dashboard`): shows assigned bookings, plumber trust score, and controls to accept/reject/complete bookings; UI typically exposes a federated learning “simulate update” control.
  - **Admin** (`/admin/dashboard`): aggregates global stats, recent bookings, fraud alerts, rating distributions, and federated learning metrics (`federated_orchestrator.get_stats()` and `fraud_detector.get_metrics()`).

### Booking lifecycle with fraud detection

- Bookings are created via `POST /api/bookings/create` (customer-only JSON endpoint):
  - Persists a `Booking` row.
  - Derives a feature vector (`booking_data`) combining price, historical counts, cancellation rates, and time-to-booking.
  - Calls `fraud_detector.detect_anomaly(booking_data)`.
    - If the ML model is untrained, the detector falls back to `_rule_based_detection`, with explicit support for price manipulation, fake bookings, rush scams, and suspicious patterns.
  - When `is_fraud` is `True` with `risk_score > 60`, creates a `FraudAlert` tied to the booking and actors.
  - Returns JSON including `fraud_check` payload and a `rule_price_deviation` convenience flag.

- Fraud can also be checked manually via `POST /api/fraud/detect`, which forwards arbitrary booking-like data to `fraud_detector.detect_anomaly` and returns the structured result.

Keep the shape of the `fraud_detector` response stable (`is_fraud`, `risk_score`, `fraud_type`, `description`) if you change internals, as templates and APIs depend on this contract.

### Trust scoring and behavior penalties

The trust system is built on `TrustScore` rows and the `trust_scorer` helper:

- On registration (`/register`):
  - Every new user gets an associated `TrustScore` row; plumbers receive an additional plumber-specific `TrustScore` attached to their `Plumber` record.

- Booking cancellation and rejection flows:
  - **Customer cancels after acceptance** (`POST /api/bookings/<booking_id>/cancel`):
    - If status is `accepted`, the customer’s `TrustScore` anomaly score and dispute count are increased.
    - `trust_scorer.calculate_trust_score(metrics)` recomputes `overall_score` using completion rate, review authenticity, response time score, dispute count, and anomaly score.
    - If the customer has more than one cancellation total, their `overall_score` is nudged down slightly even for earlier-stage cancellations.
  - **Plumber rejects bookings excessively** (`POST /api/bookings/<booking_id>/reject`):
    - Counts all cancellations by that plumber; after the first, each additional rejection generates a `FraudAlert` with increasing risk.
    - The plumber’s `TrustScore` anomaly score and dispute count are increased; `trust_scorer.calculate_trust_score` recomputes `overall_score`.

- Review submission (`POST /api/bookings/<booking_id>/review`):
  - Customers can rate completed bookings and leave review text.
  - Plumber `TrustScore.review_authenticity` is recomputed using `trust_scorer.estimate_review_authenticity(reviews)` over all completed, rated bookings.
  - The plumber’s `overall_score` is updated via `calculate_trust_score`.

The weights and trust level thresholds are defined centrally in `TrustScorer`; keep them consistent with the description in `README.md`/`USER_GUIDE.md` when adjusting.

### Federated learning pipeline

Federated learning is simulated via `federated_orchestrator` plus DB models `LocalModelUpdate` and `GlobalModel`:

- Clients submit local model updates via `POST /api/federated/submit-update`:
  - Requires login; uses `current_user.id` as `client_id`.
  - Expects JSON fields `weights` (list of floats) and `num_samples`.
  - Stores the update in-memory (`pending_updates`) and persists a `LocalModelUpdate` row with the current global version and serialized weights.

- Admin can trigger aggregation via `POST /api/federated/aggregate`:
  - Guarded by `@role_required('admin')`.
  - Calls `federated_orchestrator.aggregate_updates()`.
    - Implements FedAvg weighted by `num_samples`.
    - Requires at least `min_updates_for_aggregation` updates (default `3`).
  - On success, persists a new `GlobalModel` row with version, serialized weights, and aggregated update count.

- Clients fetch the current model via `GET /api/federated/global-model`:
  - Returns JSON with `version`, `weights`, `timestamp`, and `pending_updates`.

The dashboards surface basic statistics by calling `federated_orchestrator.get_stats()` and introspecting `GlobalModel`.

### Templates & presentation

- All HTML views extend `templates/base.html` and use Bootstrap 5 + Chart.js.
- Dashboards pull their data directly from SQLAlchemy queries in `app.py`:
  - Admin charts use precomputed dictionaries for booking status counts, fraud risk distribution, and rating distribution.
  - Customer and plumber dashboards render bookings and trust metrics for the current actor.
- A custom Jinja2 filter `to_ist` in `app.py` converts UTC timestamps to IST (UTC+5:30) for display.

When adding new data to dashboards, prefer computing aggregate structures in `app.py` and passing them into templates rather than embedding complex logic in Jinja.


## How this file relates to existing docs

- `README.md` – Primary technical and research documentation: overall purpose, architecture diagrams, key innovations, detailed feature explanations, and project structure. When in doubt about high-level intent, check there first.
- `USER_GUIDE.md` – Walkthrough of the platform from the perspective of customer, plumber, and admin, plus API testing snippets and demo tips.
- `FRAUD_DETECTION_EXPLAINED.md` and `REPORT.md` – Deeper explanations of the fraud and federated learning methodology and research context.

Keep this `WARP.md` focused on concrete project-specific workflows and architecture; broader conceptual explanations should continue to live in the existing documentation files.