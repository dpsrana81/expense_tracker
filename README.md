# ExpenseFlow — Cloud Expense Tracker System

A production-style expense and budget tracker built with **Python Flask, MySQL, Docker, and a Bootstrap 5 dashboard**, designed according to the provided project guide (cloud-native, JWT-secured, CI/CD-ready).

This repository is a complete, working implementation: authentication, dashboard, full expense/income/budget management, reporting, and an admin panel are all functional out of the box. AWS, Kubernetes, Jenkins, and monitoring configs are included as deployment-ready templates so you can take the same codebase from your laptop to production.

## 1. Features

- **Authentication** — registration, login, logout, JWT access/refresh tokens stored in httpOnly cookies, bcrypt password hashing. The first user to register automatically becomes an **admin**.
- **Expense management** — full CRUD, search, filter by category/month/year, pagination, payment method, notes.
- **Income management** — full CRUD with categorized sources.
- **Categories** — pre-seeded defaults per user (Food, Transport, Housing, etc.) plus custom categories.
- **Budgets** — per-category monthly limits with live spent/remaining calculation and progress bars.
- **Dashboard** — total income/expense/net savings, 6-month trend chart, category breakdown doughnut chart, recent expenses, budget alerts (Chart.js).
- **Reports** — CSV and PDF export of expenses for any month/year.
- **Receipt uploads** — image/PDF upload endpoint, stored locally by default with a clear extension point for Amazon S3.
- **Admin dashboard** — platform-wide stats, user list with enable/disable toggle, audit log viewer.
- **Audit logging** — every login, registration, and create/update/delete action is recorded.
- **Professional UI** — custom design system (not default Bootstrap look), responsive sidebar layout, toast notifications, modals, empty states.

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask, Flask-JWT-Extended, SQLAlchemy, Flask-Migrate, Marshmallow, Bcrypt, Gunicorn |
| Frontend | HTML5, CSS3 (custom design system), Bootstrap 5, Bootstrap Icons, vanilla JavaScript, Chart.js |
| Database | MySQL 8 (production / Docker) or SQLite (zero-config local dev) |
| Cloud (templates included) | AWS EC2, RDS, S3, SES, IAM, CloudWatch |
| DevOps | Docker, Docker Compose, Nginx, GitHub Actions, Jenkins, Kubernetes, Prometheus, Grafana |

## 3. Project Structure

```
expense-tracker/
├── backend/                 # Flask application (API + server-rendered frontend)
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (User, Expense, Income, Category, Budget, AuditLog)
│   │   ├── routes/          # Blueprints: auth, expenses, income, categories, budgets, dashboard, reports, admin, uploads, pages
│   │   ├── schemas/         # Marshmallow validation schemas
│   │   ├── static/          # css/, js/, uploads/
│   │   ├── templates/       # Jinja2 pages (login, dashboard, expenses, income, budgets, reports, admin)
│   │   ├── utils/           # decorators & helpers
│   │   ├── config.py
│   │   └── __init__.py      # app factory
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── run.py
│   └── .env.example
├── database/init.sql        # MySQL bootstrap script
├── nginx/nginx.conf         # Reverse proxy config
├── kubernetes/              # Deployment, Service, HPA, Secrets, Ingress manifests
├── monitoring/              # Prometheus + Grafana docker-compose addon
├── .github/workflows/       # GitHub Actions CI/CD pipeline
├── Jenkinsfile               # Alternative Jenkins pipeline
├── docker-compose.yml        # MySQL + backend + Nginx, all together
└── docs/                     # API reference & deployment guide
```

## 4. Quick Start (local, no Docker, SQLite)

The fastest way to see it running:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open **http://localhost:5000** — register an account (the first account becomes an admin automatically), and you're in.

## 5. Run with Docker Compose (MySQL + Nginx, production-like)

```bash
cp backend/.env.example backend/.env
# edit backend/.env and set real SECRET_KEY / JWT_SECRET_KEY values

docker compose up --build -d
```

- App via Nginx: **http://localhost**
- App directly: **http://localhost:5000**
- MySQL: localhost:3306 (credentials from `docker-compose.yml` / `.env`)

To switch the Flask app from SQLite to MySQL manually (outside Docker), set in `backend/.env`:

```
DATABASE_URL=mysql+pymysql://expense_user:expense_pass@localhost:3306/expense_tracker
```

## 6. Database Migrations

This project uses Flask-Migrate (Alembic). `db.create_all()` runs automatically on first launch for convenience, but for ongoing schema changes use migrations:

```bash
cd backend
flask db init        # only once
flask db migrate -m "describe your change"
flask db upgrade
```

## 7. Deploying to AWS (per the original project guide)

1. **RDS** — create a MySQL 8 instance, set `DATABASE_URL` to its endpoint.
2. **S3** — create a bucket for receipts, set `USE_S3=True`, `AWS_S3_BUCKET`, `AWS_REGION`, and configure IAM credentials (the upload route in `app/routes/uploads.py` has a clear extension point for swapping local storage for `boto3` S3 calls).
3. **SES** — verify a sending domain/address for budget-alert emails.
4. **EC2** — install Docker, copy this repo, run `docker compose up -d`, and put **Nginx** (already included) in front with HTTPS via Certbot.
5. **CI/CD** — push to `main` to trigger `.github/workflows/ci-cd.yml` (build → push to Docker Hub → SSH deploy to EC2), or use the included `Jenkinsfile`.
6. **Kubernetes (optional)** — apply the manifests in `kubernetes/` to run the backend behind an autoscaling Deployment + Ingress instead of a single EC2 box.
7. **Monitoring** — `docker compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d` brings up Prometheus + Grafana; CloudWatch can be wired in via the AWS CloudWatch Agent on EC2.

See `docs/DEPLOYMENT.md` for the detailed step-by-step version of all of the above.

## 8. API Reference

Full endpoint list, request/response shapes, and auth notes are in `docs/API.md`.

## 9. Default Admin Behavior

There's no separate admin signup — the very first account created in a fresh database is automatically promoted to `role: admin` and unlocks `/admin`. Every subsequent signup is a normal `user`. An existing admin can't currently demote/promote other users from the UI (intentionally out of scope for v1) — that's the one item flagged as a natural "next step" if you extend this further.

## 10. Security Notes

- Passwords hashed with bcrypt, never stored or logged in plain text.
- JWT access tokens live in httpOnly cookies (`JWT_COOKIE_SECURE=True` in production forces HTTPS-only cookies).
- All `/api/*` write endpoints are scoped to `get_jwt_identity()` — users can only ever read/modify their own data; admin-only endpoints use a dedicated `@admin_required` decorator.
- File uploads are limited to 5MB and restricted to `png/jpg/jpeg/pdf`.
- Set real, random `SECRET_KEY` / `JWT_SECRET_KEY` values before deploying — the defaults in `.env.example` are for local development only.
