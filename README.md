# TIN Regulatory Validation Platform

An AI-powered Tax Identification Number (TIN) validation platform that automatically extracts TIN rules from OECD documents and validates customer TINs against those rules.

## Architecture

```
tin-regulatory-validation-platform/
├── backend/          # Django REST Framework API
├── frontend/         # React + TypeScript + Vite SPA
├── docker-compose.yml
├── .env.example
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 4.2, Django REST Framework |
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Database | PostgreSQL 15 |
| Cache / Queue | Redis 7, Celery |
| Auth | JWT (djangorestframework-simplejwt) |
| API Docs | Swagger / OpenAPI (drf-spectacular) |
| Containers | Docker, Docker Compose |

## Features

### Backend
- **JWT Authentication** – Register, login, token refresh
- **Document Upload** – Upload OECD PDF documents (up to 20MB)
- **PDF Processing Pipeline** – Celery worker: PDF → text extraction → chunking → rule extraction → DB storage
- **TIN Validation Engine** – Validate TINs using regex patterns, length constraints, and checksum rules
- **Batch Validation** – Upload a CSV with multiple TINs for background processing
- **Report Generation** – Download validation results as CSV or JSON
- **OpenAPI / Swagger Docs** – Available at `/api/docs/`

### Frontend
- **Dashboard** – Overview stats, validation rate, recent activity
- **Document Upload** – Upload OECD PDFs with real-time status polling
- **Rule Viewer** – Browse extracted TIN rules filtered by country
- **TIN Validation Tool** – Single TIN validation with detailed explanation
- **Batch CSV Upload** – Upload and process multiple TINs
- **Validation Results** – History with export to CSV/JSON

## Quick Start

### Prerequisites
- Docker & Docker Compose

### 1. Clone and configure

```bash
git clone <repo-url>
cd tin-regulatory-validation-platform
cp .env.example .env
```

### 2. Start all services

```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Django API** on port 8000
- **Celery Worker** for background jobs
- **React Frontend** on port 3000

### 3. Access the application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000/api/v1/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

### 4. Create a superuser (optional)

```bash
docker-compose exec backend python manage.py createsuperuser
```

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your local settings (DB_HOST=localhost, etc.)

# Run migrations
python manage.py migrate

# Seed default TIN rules
python manage.py seed_tin_rules

# Start development server
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs at http://localhost:5173 and proxies `/api` to `http://localhost:8000`.

## API Documentation

Full OpenAPI 3.0 schema available at:
- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`
- Raw schema: `GET /api/schema/`

### Core Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login (returns JWT) |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |
| GET/PATCH | `/api/v1/auth/me/` | Get/update current user |

#### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/documents/` | List uploaded documents |
| POST | `/api/v1/documents/upload/` | Upload PDF |
| GET | `/api/v1/documents/{id}/` | Get document details |
| DELETE | `/api/v1/documents/{id}/` | Delete document |

#### TIN Rules
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rules/` | List all rules |
| GET | `/api/v1/rules/?country=US` | Filter by country |
| GET | `/api/v1/rules/countries/` | List all countries |
| GET | `/api/v1/rules/{id}/` | Get rule details |

#### Validation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/validation/validate/` | Validate single TIN |
| GET | `/api/v1/validation/results/` | List validation history |
| POST | `/api/v1/validation/batch/upload/` | Upload CSV batch |
| GET | `/api/v1/validation/batch/` | List batch jobs |
| GET | `/api/v1/validation/batch/{id}/results/` | Batch results |

#### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports/` | List reports |
| POST | `/api/v1/reports/generate/` | Generate report |
| GET | `/api/v1/reports/{id}/download/` | Download report |

### Example: Validate a TIN

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Validate TIN
curl -X POST http://localhost:8000/api/v1/validation/validate/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "tin": "123-45-6789"}'
```

**Response:**
```json
{
  "id": 1,
  "country_code": "US",
  "country_name": "United States",
  "tin": "123-45-6789",
  "is_valid": true,
  "status": "valid",
  "explanation": "TIN \"123-45-6789\" is valid for United States.\n✓ Rule [format]: US SSN format: XXX-XX-XXXX (9 digits)",
  "matched_rules": [...],
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Supported Countries

The platform ships with pre-seeded TIN rules for:

| Country | Code | Format |
|---------|------|--------|
| United States | US | SSN (XXX-XX-XXXX), EIN (XX-XXXXXXX), ITIN |
| United Kingdom | GB | UTR (10 digits), NI Number |
| Germany | DE | Steuer-ID (11 digits) |
| France | FR | Numéro fiscal (13 digits) |
| Canada | CA | SIN (XXX-XXX-XXX) |
| Australia | AU | TFN (8-9 digits) |
| India | IN | PAN (ABCDE1234F) |
| China | CN | Resident ID (18 characters) |
| Japan | JP | My Number (12 digits) |
| Netherlands | NL | BSN (9 digits) |

## Batch CSV Format

```csv
country,tin
US,123-45-6789
GB,1234567890
DE,12345678901
```

## Database Models

- **User** – Authentication and user management
- **RuleSourceDocument** – Uploaded OECD PDF documents
- **Country** – Country with ISO alpha-2 code
- **TinRule** – Validation rule (regex, length, type)
- **ValidationResult** – Result of a TIN validation
- **ValidationBatch** – Batch validation job
- **Report** – Generated CSV/JSON report

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT