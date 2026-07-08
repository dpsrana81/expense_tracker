-- This script runs automatically when the MySQL container starts for the
-- first time. The Flask app creates all tables itself via SQLAlchemy
-- (db.create_all()) or Alembic migrations (flask db upgrade), so this file
-- just ensures the database and character set are ready to go.

CREATE DATABASE IF NOT EXISTS expense_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
