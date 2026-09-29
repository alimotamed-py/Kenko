# Kenko

> [!WARNING]
> **Disclaimer:** Kenko is an educational and experimental project and has **no medical or clinical validity**. Its predictions and recommendations are for demonstration purposes only and **must not be used for medical diagnosis, treatment, or clinical decision-making**.

<div align="center">

  <img src="docs/Kenko.png" alt="Kenko" width="700">

  <h1>Kenko</h1>

  <p>
    AI-Powered Health Risk Assessment Platform
  </p>

</div>

---

## About The Project

**Kenko** is an AI-powered health risk assessment platform that combines **Machine Learning** with a modern backend architecture to analyze health-related data, assess potential disease risks, and provide general health recommendations.

The platform is designed with a **scalable and modular architecture**, allowing different health conditions and Machine Learning models to be integrated as the project evolves.

Kenko provides a complete backend workflow for health risk assessment, including:

* User authentication
* Secure health data handling
* Input validation
* Machine Learning inference
* Risk assessment
* General health recommendations
* Prediction history
* API-based access to prediction services

The system separates the API layer, business logic, Machine Learning services, authentication, database, and infrastructure components to keep the project maintainable and extensible.

---

## Project Goals

The main goals of Kenko are:

* Build a scalable backend for AI-powered health applications.
* Integrate Machine Learning models into a production-oriented API architecture.
* Provide a structured workflow for health risk assessment.
* Implement secure user authentication and session management.
* Store and manage users' prediction history.
* Provide general recommendations based on submitted health information.
* Make it easy to integrate additional Machine Learning models in the future.
* Practice real-world backend, Machine Learning, security, database, and deployment concepts in a single project.

---

## Services & Features

### 1. Health Risk Assessment

Kenko accepts structured health-related information through REST API endpoints and processes the submitted data using Machine Learning models.

The prediction workflow includes:

1. Validate the incoming request.
2. Authenticate the user.
3. Validate and transform categorical values.
4. Prepare the input features.
5. Load the appropriate Machine Learning model.
6. Generate a prediction.
7. Calculate the application-level risk category.
8. Generate general recommendations.
9. Store the prediction history.
10. Return a structured API response.

---

### 2. User Authentication

Kenko uses phone-based authentication with OTP verification.

Authentication includes:

* Phone number validation
* OTP generation
* OTP expiration
* OTP verification
* OTP attempt protection
* Access tokens
* Refresh tokens
* Token rotation
* Session management
* Logout and token revocation

---

### 3. Secure Authentication Cookies

Authentication tokens are stored using **HttpOnly cookies** to reduce exposure to client-side JavaScript.

The authentication system also uses:

* Secure cookie configuration
* SameSite cookie policies
* CSRF protection
* Refresh-token rotation
* Session identifiers
* Token expiration
* Token revocation

---

### 4. Rate Limiting

Redis is used to protect authentication-related endpoints against excessive requests.

Rate limiting is applied to operations such as:

* OTP requests
* OTP verification attempts
* Authentication-related actions

---

### 5. Prediction History

Authenticated users can access their previous prediction records.

The history service provides:

* Prediction history listing
* Pagination
* Individual prediction details
* Prediction deletion
* User-specific data isolation

Users can only access their own prediction history.

---

### 6. General Health Recommendations

Based on submitted health information and prediction results, Kenko can provide general educational recommendations.

Examples include recommendations related to:

* Physical activity
* Sleep
* Stress management
* Lifestyle habits
* General health monitoring

These recommendations are informational and are not intended to replace professional medical advice.

---

### 7. PostgreSQL Database

PostgreSQL is used as the primary relational database.

The database stores application data such as:

* Users
* Prediction history
* Timestamps
* Authentication-related information

Database schema changes are managed using **Alembic migrations**.

---

### 8. Redis

Redis is used as a supporting service for temporary and fast-access data.

Current use cases include:

* OTP storage
* OTP expiration
* Rate limiting
* CSRF token storage
* Session-related temporary data

---

## How Kenko Works

The general system workflow is:

```text
Client
   │
   ▼
FastAPI
   │
   ├── Authentication
   │      ├── OTP
   │      ├── JWT
   │      └── CSRF
   │
   ├── Validation
   │
   ├── Prediction Service
   │      │
   │      └── Machine Learning Model
   │
   ├── Risk Assessment
   │
   ├── Recommendations
   │
   └── Prediction History
          │
          ├── PostgreSQL
          └── Redis
```

---

## Prediction Flow

A typical prediction request follows this process:

```text
User
 │
 ▼
Authentication
 │
 ▼
Input Validation
 │
 ▼
Feature Encoding
 │
 ▼
Feature Preprocessing
 │
 ▼
Machine Learning Model
 │
 ▼
Prediction
 │
 ▼
Risk Assessment
 │
 ▼
Recommendations
 │
 ▼
Store Prediction History
 │
 ▼
API Response
```

---

## Machine Learning

Machine Learning is a core component of Kenko.

The architecture is designed so that Machine Learning models can be added or replaced without requiring major changes to the API layer.

The ML workflow can include:

* Dataset preparation
* Exploratory Data Analysis
* Data cleaning
* Feature preprocessing
* Categorical encoding
* Feature engineering
* Train/test splitting
* Model training
* Model comparison
* Evaluation
* Model serialization
* API inference

The trained models are stored separately from the backend application code and loaded by the prediction service when required.

### Model Integration

Each prediction service is responsible for:

* Loading the required model
* Preparing incoming features
* Applying the required preprocessing
* Running inference
* Converting the result into an API-friendly format

---

## Risk Assessment

Kenko converts model output into application-level risk categories.

The risk classification is intended for application presentation and user experience.

It is **not a clinically validated risk scoring system** and should not be interpreted as a medical risk assessment.

---

## Authentication & Security

Security is an important part of the backend architecture.

### JWT Authentication

JSON Web Tokens are used for authenticated sessions.

The system supports:

* Access tokens
* Refresh tokens
* Token expiration
* Unique token identifiers
* Session identifiers
* Refresh-token rotation
* Token revocation

### HttpOnly Cookies

Authentication tokens are stored in HttpOnly cookies so they cannot be directly accessed by JavaScript running in the browser.

### CSRF Protection

CSRF protection is implemented for authenticated state-changing requests.

### OTP Protection

OTP authentication includes:

* Expiration
* Verification limits
* Request cooldown
* Failed-attempt tracking
* Temporary blocking

### User Data Isolation

Prediction history is associated with authenticated users, and access is restricted to the owner of the data.

---

## API Endpoints

The API is versioned under:

```text
/api/v1
```

### Authentication

| Method | Endpoint                   | Description                    | Authentication |
| ------ | -------------------------- | ------------------------------ | -------------- |
| POST   | `/api/v1/auth/request-otp` | Request an OTP                 | No             |
| POST   | `/api/v1/auth/verify-otp`  | Verify OTP and authenticate    | No             |
| GET    | `/api/v1/auth/me`          | Get current user information   | Yes            |
| POST   | `/api/v1/auth/refresh`     | Refresh authentication session | Refresh Token  |
| POST   | `/api/v1/auth/logout`      | Logout and revoke session      | Refresh Token  |

### Prediction

| Method | Endpoint              | Description                  | Authentication |
| ------ | --------------------- | ---------------------------- | -------------- |
| POST   | `/api/v1/predict/...` | Run a health risk prediction | Yes            |

Additional prediction endpoints can be added as new Machine Learning models are integrated.

### Prediction History

| Method | Endpoint                       | Description                   | Authentication |
| ------ | ------------------------------ | ----------------------------- | -------------- |
| GET    | `/api/v1/history`              | Get user's prediction history | Yes            |
| GET    | `/api/v1/history/{history_id}` | Get a prediction record       | Yes            |
| DELETE | `/api/v1/history/{history_id}` | Delete a prediction record    | Yes            |

---

## API Response Design

Kenko uses structured API responses to make communication between the backend and future clients predictable and consistent.

A prediction response can contain information such as:

```json
{
  "success": true,
  "prediction": 1,
  "probability": 0.82,
  "risk_level": "high",
  "recommendations": [
    "Consider discussing your health information with a healthcare professional."
  ]
}
```

The exact prediction fields depend on the Machine Learning model and prediction service being used.

---

## Error Handling

Kenko provides centralized error handling for common API errors.

The API handles cases such as:

* Validation errors
* Authentication errors
* Authorization errors
* Invalid tokens
* Expired tokens
* Rate-limit violations
* Business logic errors
* Unexpected server errors

Validation errors follow a structured format similar to:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data."
  }
}
```

---

## Technology Stack

### Backend

* **Python 3.12+**
* **FastAPI**
* **Pydantic**
* **SQLModel**
* **Alembic**

### Database

* **PostgreSQL**

### Cache & Temporary Data

* **Redis**

### Authentication & Security

* **JWT**
* **HttpOnly Cookies**
* **CSRF Protection**
* **OTP Authentication**
* **Rate Limiting**

### Machine Learning

* **scikit-learn**
* **XGBoost**
* **Pandas**
* **NumPy**
* **Joblib**

### Infrastructure

* **Docker**
* **Docker Compose**
* **uv**

---

## Project Architecture

Kenko follows a modular backend architecture.

```text
API Layer
    │
    ▼
Schemas & Validation
    │
    ▼
Services / Business Logic
    │
    ├── Authentication
    ├── Prediction
    ├── Risk Assessment
    ├── Recommendations
    ├── OTP
    ├── Rate Limiting
    └── CSRF
    │
    ▼
Data Layer
    │
    ├── PostgreSQL
    └── Redis

Machine Learning Layer
    │
    ├── Preprocessing
    ├── Models
    └── Inference
```

---

## Project Structure

```text
Kenko/
│
├── Backend/
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   └── app/
│       ├── api/
│       │   └── routes/
│       │
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── exceptions.py
│       │   ├── logging.py
│       │   └── redis.py
│       │
│       ├── models/
│       ├── schemas/
│       ├── security/
│       ├── services/
│       ├── dependencies.py
│       └── main.py
│
├── ML/
│   ├── data/
│   ├── notebook/
│   └── ML models/
│
├── src/
│   └── kenko/
│
├── docs/
│   └── Kenko.png
│
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/alimotamed-py/Kenko.git
cd Kenko
```

### 2. Install Dependencies

Kenko uses `uv` for Python dependency management.

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root and configure the required environment variables according to your local or deployment environment.

> **Note:** Environment variable values and secrets are intentionally not included in this README.

### 4. Database Migrations

Apply the existing migrations:

```bash
uv run alembic upgrade head
```

---

## Running The API

Run the development server with:

```bash
uv run uvicorn app.main:app --app-dir Backend --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Running With Docker

Kenko includes Docker support for running the application together with its infrastructure services.

Build and start the containers:

```bash
docker compose up --build
```

The main services are:

```text
api
postgres
redis
```

The API is exposed on:

```text
http://127.0.0.1:8002
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8002/docs
```

### ReDoc

```text
http://127.0.0.1:8002/redoc
```

These interfaces can be used to inspect available endpoints, request schemas, response schemas, authentication requirements, and API behavior.

---

## Development Workflow

The project follows a development workflow that separates Machine Learning experimentation from backend implementation.

### Machine Learning

```text
Dataset
   ↓
EDA
   ↓
Data Cleaning
   ↓
Preprocessing
   ↓
Feature Engineering
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Model Serialization
```

### Backend

```text
API Request
   ↓
Validation
   ↓
Authentication
   ↓
Business Logic
   ↓
ML Inference
   ↓
Database
   ↓
API Response
```

This separation allows Machine Learning experimentation and backend development to evolve independently.

---

## Future Development

The project is designed to evolve into a broader health-focused AI platform.

Potential future improvements include:

* Integration of additional Machine Learning models
* Support for multiple health conditions
* Improved model management
* Model versioning
* Automated model evaluation
* More advanced feature engineering pipelines
* Improved recommendation systems
* Background processing with Celery
* Notification services
* More comprehensive automated testing
* CI/CD pipelines
* Monitoring and observability
* API performance optimization
* Frontend integration
* Improved deployment infrastructure

---

## Development Philosophy

Kenko is being developed with an emphasis on:

* Clean architecture
* Separation of concerns
* Secure authentication
* Maintainable code
* Reusable services
* API consistency
* Machine Learning integration
* Scalability
* Practical backend engineering

The project is also intended as a practical learning and portfolio project that demonstrates how Machine Learning can be integrated into a real backend application.

---

## License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for more information.

---

## Author

**Ali Motamed**

GitHub: [@alimotamed-py](https://github.com/alimotamed-py)

---

## Disclaimer

Kenko is an educational and experimental software project.

The system has **no medical or clinical validity**. Predictions, risk categories, and recommendations generated by the system are intended solely for demonstration and educational purposes.

They must not be used as a substitute for professional medical advice, diagnosis, treatment, or clinical decision-making.
