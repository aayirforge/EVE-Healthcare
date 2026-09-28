# EVE Healthcare - Diagnostic Centre Booking & Payment API

A robust, production-ready backend service for diagnostic healthcare operations, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, and **Docker**.

---

## Table of Contents

- [How to run the project locally](#how-to-run-the-project-locally)
- [API endpoints and example requests](#api-endpoints-and-example-requests)
- [Database/schema design](#databaseschema-design)
- [Important assumptions made](#important-assumptions-made)
- [What I would improve if I had more time](#what-i-would-improve-if-i-had-more-time)

---

## How to run the project locally

You can run the project either using **Docker** (recommended for zero manual setup) or locally with a **Python virtual environment**.

### Option A: Running with Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd EVE-Healthcare
   ```

2. **Start the application and PostgreSQL database:**
   ```bash
   docker compose up --build
   ```
   *(or `sudo docker compose up --build` if your user is not yet in the docker group)*

   This single command:
   - Starts a dedicated **PostgreSQL 16** container (`eve_healthcare_db`) with volume persistence and health checks.
   - Automatically runs all Alembic database migrations (`alembic upgrade head`).
   - Launches the **FastAPI ASGI server** (`eve_healthcare_api`) on `http://127.0.0.1:8000`.

3. **Stop the containers:**
   ```bash
   docker compose down
   ```

---

### Option B: Running Locally with Python Virtual Environment

1. **Prerequisites:**
   - Python 3.12+ (or Python 3.14)
   - PostgreSQL running locally

2. **Set up PostgreSQL Database:**
   ```sql
   CREATE USER eve_user WITH PASSWORD 'eve_password';
   CREATE DATABASE eve_healthcare OWNER eve_user;
   GRANT ALL PRIVILEGES ON DATABASE eve_healthcare TO eve_user;
   ```

3. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Environment File:**
   ```bash
   cp .env.example .env
   ```

6. **Apply Database Migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the FastAPI Application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The application will be accessible at `http://127.0.0.1:8000`.

---

### Running the Automated Test Suite

All 49 unit and integration tests run against PostgreSQL with isolated transactions and automatic rollbacks (no SQLite mocking discrepancies):

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Run tests
pytest -v
```

---

## API endpoints and example requests

Interactive documentation is available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

### Summary of Endpoints

| Category | Method | Endpoint | Description | Auth Required |
|---|---|---|---|---|
| **Auth** | `POST` | `/auth/signup` | Register a new user | No |
| **Auth** | `POST` | `/auth/login` | Authenticate and obtain JWT access token | No |
| **Auth** | `GET` | `/auth/me` | Retrieve profile of authenticated user | Yes |
| **Tests** | `POST` | `/tests/` | Create a new diagnostic test | Yes |
| **Tests** | `GET` | `/tests/` | List diagnostic tests (Paginated) | No |
| **Tests** | `GET` | `/tests/{test_id}` | Get details of a diagnostic test | No |
| **Centres** | `POST` | `/centres/` | Register a new diagnostic centre | Yes |
| **Centres** | `GET` | `/centres/` | List centres with available tests (Paginated) | No |
| **Centres** | `GET` | `/centres/{centre_id}` | Get details of a centre and its tests | No |
| **Centres** | `POST` | `/centres/{centre_id}/tests` | Associate a test with centre (with custom pricing) | Yes |
| **Centres** | `DELETE` | `/centres/{centre_id}/tests/{test_id}` | Remove a test association from a centre | Yes |
| **Bookings** | `POST` | `/bookings/` | Book a diagnostic test at a centre | Yes |
| **Bookings** | `GET` | `/bookings/` | List current user's bookings (Paginated) | Yes |
| **Bookings** | `GET` | `/bookings/{booking_id}` | Get specific booking details | Yes (Owner) |
| **Bookings** | `POST` | `/bookings/{booking_id}/cancel` | Cancel a pending booking | Yes (Owner) |
| **Payments** | `POST` | `/payments/` | Simulate payment (`SUCCESS` or `FAILED`) | Yes (Owner) |
| **Payments** | `POST` | `/payments/webhook/` | Idempotent payment gateway webhook receiver | No |
| **Health** | `GET` | `/health` | Health check endpoint | No |

---

### Example Requests & Responses

#### 1. User Signup
```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.doe@example.com",
    "password": "SecurePassword123!",
    "full_name": "Jane Doe"
  }'
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "email": "jane.doe@example.com",
  "full_name": "Jane Doe",
  "created_at": "2026-09-28T02:00:00Z"
}
```

#### 2. User Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.doe@example.com",
    "password": "SecurePassword123!"
  }'
```
**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

#### 3. Create a Diagnostic Test
```bash
curl -X POST http://127.0.0.1:8000/tests/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Complete Blood Count",
    "description": "Comprehensive screening of blood cells",
    "price": "450.00"
  }'
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "name": "Complete Blood Count",
  "description": "Comprehensive screening of blood cells",
  "price": "450.00",
  "created_at": "2026-09-28T02:05:00Z"
}
```

#### 4. Create a Diagnostic Centre
```bash
curl -X POST http://127.0.0.1:8000/centres/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Apollo Clinic",
    "location": "Indiranagar, Bangalore"
  }'
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "name": "Apollo Clinic",
  "location": "Indiranagar, Bangalore",
  "created_at": "2026-09-28T02:10:00Z",
  "available_tests": []
}
```

#### 5. Link Test to Centre with Custom Pricing
```bash
curl -X POST http://127.0.0.1:8000/centres/1/tests \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": 1,
    "custom_price": "400.00"
  }'
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "name": "Apollo Clinic",
  "location": "Indiranagar, Bangalore",
  "created_at": "2026-09-28T02:10:00Z",
  "available_tests": [
    {
      "test_id": 1,
      "name": "Complete Blood Count",
      "description": "Comprehensive screening of blood cells",
      "base_price": "450.00",
      "effective_price": "400.00",
      "custom_price": "400.00"
    }
  ]
}
```

#### 6. Book a Diagnostic Test
```bash
curl -X POST http://127.0.0.1:8000/bookings/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "centre_id": 1,
    "test_id": 1,
    "appointment_time": "2026-10-15T10:30:00Z"
  }'
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "user_id": 1,
  "centre_id": 1,
  "test_id": 1,
  "appointment_time": "2026-10-15T10:30:00Z",
  "amount": "400.00",
  "status": "PENDING",
  "created_at": "2026-09-28T02:15:00Z",
  "centre_name": "Apollo Clinic",
  "test_name": "Complete Blood Count"
}
```

#### 7. Simulate Payment
```bash
curl -X POST http://127.0.0.1:8000/payments/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "status": "SUCCESS"
  }'
```
**Response (`200 OK`):**
```json
{
  "id": 1,
  "booking_id": 1,
  "amount": "400.00",
  "status": "SUCCESS",
  "provider_payment_id": "sim_pay_f8c12a3d",
  "created_at": "2026-09-28T02:16:00Z",
  "booking_status": "CONFIRMED"
}
```

#### 8. Payment Webhook (Idempotent)
```bash
curl -X POST http://127.0.0.1:8000/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_gateway_1001",
    "booking_id": 1,
    "payment_status": "SUCCESS",
    "provider_payment_id": "pay_stripe_1001"
  }'
```
- **First Call (`200 OK`):**
  ```json
  {
    "status": "processed",
    "message": "Webhook event processed successfully",
    "event_id": "evt_gateway_1001",
    "booking_id": 1,
    "booking_status": "CONFIRMED"
  }
  ```
- **Duplicate Call (`200 OK` - Idempotently Ignored):**
  ```json
  {
    "status": "ignored",
    "message": "Duplicate event already processed",
    "event_id": "evt_gateway_1001",
    "booking_id": 1,
    "booking_status": "CONFIRMED"
  }
  ```

#### 9. Cancel a Booking
```bash
curl -X POST http://127.0.0.1:8000/bookings/1/cancel \
  -H "Authorization: Bearer <TOKEN>"
```
**Response (`200 OK`):**
```json
{
  "id": 1,
  "user_id": 1,
  "centre_id": 1,
  "test_id": 1,
  "appointment_time": "2026-10-15T10:30:00Z",
  "amount": "400.00",
  "status": "CANCELLED",
  "created_at": "2026-09-28T02:15:00Z",
  "centre_name": "Apollo Clinic",
  "test_name": "Complete Blood Count"
}
```


---

## Database/schema design

The database schema is implemented in PostgreSQL using SQLAlchemy 2.0 and version-controlled with Alembic migrations. It enforces strict relational integrity, check constraints, unique constraints, and foreign key cascading.

```
                    ┌─────────────────┐
                    │      users      │
                    └────────┬────────┘
                             │ 1
                             │
                             │ N
                    ┌────────┴────────┐
                    │    bookings     ├─────────────┐
                    └───┬─────────┬───┘             │
                      N │         │ N               │ 1
                        │         │                 │
           ┌────────────┘         └──────────┐      │ N
           │ 1                             1 │   ┌──┴───────────────┐
┌──────────┴─────────┐             ┌─────────┴───┴──────┐   │     payments      │
│ diagnostic_centres │             │  diagnostic_tests  │   └───────────────────┘
└──────────┬─────────┘             └─────────┬──────────┘
           │ 1                             1 │
           │         ┌──────────────┐        │              ┌───────────────────┐
           └─────────┤ centre_tests ├────────┘              │  webhook_events   │
                   N └──────────────┘ N                     └───────────────────┘
```

### Table Definitions

1. **`users`**
   - `id`: Integer, Primary Key, autoincrement.
   - `email`: String(255), Unique, Indexed, Not Null.
   - `hashed_password`: String(255), Not Null (bcrypt hash).
   - `full_name`: String(255), Not Null.
   - `created_at`, `updated_at`: DateTime with Timezone, Not Null.

2. **`diagnostic_centres`**
   - `id`: Integer, Primary Key, autoincrement.
   - `name`: String(255), Indexed, Not Null.
   - `location`: String(255), Not Null.
   - `created_at`, `updated_at`: DateTime with Timezone, Not Null.

3. **`diagnostic_tests`**
   - `id`: Integer, Primary Key, autoincrement.
   - `name`: String(255), Indexed, Not Null.
   - `description`: String(500), Nullable.
   - `price`: Numeric(10, 2), Check Constraint (`price >= 0`), Not Null.
   - `created_at`, `updated_at`: DateTime with Timezone, Not Null.

4. **`centre_tests`** *(Many-to-Many Association Table)*
   - `id`: Integer, Primary Key, autoincrement.
   - `centre_id`: Foreign Key (`diagnostic_centres.id`, `ON DELETE CASCADE`), Not Null.
   - `test_id`: Foreign Key (`diagnostic_tests.id`, `ON DELETE CASCADE`), Not Null.
   - `custom_price`: Numeric(10, 2), Nullable, Check Constraint (`custom_price >= 0`).
   - `UniqueConstraint("centre_id", "test_id")`: Prevents duplicate associations.

5. **`bookings`**
   - `id`: Integer, Primary Key, autoincrement.
   - `user_id`: Foreign Key (`users.id`, `ON DELETE CASCADE`), Not Null.
   - `centre_id`: Foreign Key (`diagnostic_centres.id`, `ON DELETE RESTRICT`), Not Null.
   - `test_id`: Foreign Key (`diagnostic_tests.id`, `ON DELETE RESTRICT`), Not Null.
   - `appointment_time`: DateTime with Timezone, Not Null.
   - `amount`: Numeric(10, 2), Not Null (Price snapshot captured at booking creation time).
   - `status`: String(30), Not Null, Check Constraint (`status IN ('PENDING', 'CONFIRMED', 'FAILED', 'CANCELLED')`).
   - `created_at`, `updated_at`: DateTime with Timezone, Not Null.

6. **`payments`**
   - `id`: Integer, Primary Key, autoincrement.
   - `booking_id`: Foreign Key (`bookings.id`, `ON DELETE CASCADE`), Not Null.
   - `amount`: Numeric(10, 2), Not Null.
   - `status`: String(30), Not Null, Check Constraint (`status IN ('SUCCESS', 'FAILED')`).
   - `provider_payment_id`: String(100), Nullable.
   - `idempotency_key`: String(100), Unique, Indexed, Not Null.
   - `created_at`, `updated_at`: DateTime with Timezone, Not Null.

7. **`webhook_events`**
   - `id`: Integer, Primary Key, autoincrement.
   - `event_id`: String(100), Unique, Indexed, Not Null (enforces webhook idempotency at DB level).
   - `booking_id`: Foreign Key (`bookings.id`, `ON DELETE CASCADE`), Not Null.
   - `payment_status`: String(30), Not Null.
   - `provider_payment_id`: String(100), Nullable.
   - `created_at`: DateTime with Timezone, Not Null.

---

## Important assumptions made

1. **Pricing Hierarchy & Resolution:**
   - Every diagnostic test has a global baseline price in `diagnostic_tests`.
   - Diagnostic centres can configure a `custom_price` in `centre_tests`. If a centre defines a custom price, that price is used; if `custom_price` is `NULL`, the system falls back to the test's baseline price.

2. **Immutable Snapshot Pricing:**
   - When a booking is created, the system resolves the current price and stores it permanently in `bookings.amount`. The client cannot specify or tamper with the amount in the request payload. Future price changes to the test or centre will never alter past bookings.

3. **Booking State Machine Transitions:**
   - Valid booking states: `PENDING`, `CONFIRMED`, `FAILED`, and `CANCELLED`.
   - Payments can **only** be processed for bookings in `PENDING` status. Attempting payment on already `CONFIRMED`, `FAILED`, or `CANCELLED` bookings is rejected with `400 Bad Request`.
   - Bookings can **only** be cancelled while in `PENDING` status. A `CONFIRMED` booking cannot be cancelled directly without a refund flow.

4. **Webhook Idempotency & Concurrency Safety:**
   - External gateways frequently resend webhooks on network timeouts. We assume all webhooks supply a unique `event_id`.
   - Idempotency is enforced directly at the database level via `UNIQUE(event_id)`. Re-delivering an identical webhook returns `200 OK` (`"message": "Duplicate event already processed"`), guaranteeing zero duplicate records or corrupt state transitions.

5. **Tenant Isolation & Security:**
   - Authenticated users can only view and cancel bookings that belong to them (`user_id == current_user.id`). Attempting to inspect another user's booking returns `403 Forbidden`.
   - Passwords are never stored in plaintext and are salted and hashed using `bcrypt`. Authentication uses stateless JWT tokens (`HS256`).

6. **PostgreSQL as Single Source of Truth:**
   - The system is built and tested exclusively on PostgreSQL (in development, testing, and Docker), ensuring identical behavior for check constraints, timezone handling, and transactional locking.

---

## What I would improve if I had more time

1. **Time Slot & Capacity Management:**
   - Implement discrete appointment slots (e.g., 30-minute intervals) with technician availability and maximum concurrent capacity per diagnostic centre to prevent overbooking.

2. **Real Payment Gateway Integration & Signature Verification:**
   - Integrate Stripe or Razorpay SDKs with cryptographic HMAC-SHA256 signature verification on webhook headers (`Stripe-Signature` / `X-Razorpay-Signature`) to verify payload authenticity.

3. **Asynchronous Background Processing (Celery & Redis):**
   - Offload appointment confirmation emails, SMS notifications, and PDF invoice generation to an asynchronous task queue rather than processing synchronously in HTTP requests.

4. **Role-Based Access Control (RBAC):**
   - Introduce user roles (`PATIENT`, `CENTRE_ADMIN`, `SYSTEM_SUPERADMIN`) so centre managers can update their own test pricing and schedules, while patients can only manage their bookings.

5. **Audit Logging & State Transition History:**
   - Create a dedicated `booking_status_logs` audit table tracking historical state transitions, reason codes (e.g. cancellation reasons), timestamps, and actor IDs for regulatory compliance.

6. **Rate Limiting & Throttling:**
   - Implement Redis-backed token bucket rate limiting on sensitive endpoints (e.g., `/auth/login`, `/auth/signup`, `/bookings/`) to safeguard against brute-force attacks and abuse.
