# API Reference

Base URL (local): `http://localhost:5000`

Authentication uses JWT stored in httpOnly cookies set by `/api/auth/login`. When testing with `curl`, use `-c cookies.txt -b cookies.txt` to persist the session across requests. All endpoints below (other than register/login) require an authenticated session.

## Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | `{full_name, email, password}` → creates account (first user becomes admin) |
| POST | `/api/auth/login` | `{email, password}` → sets JWT cookies |
| POST | `/api/auth/refresh` | Refresh access token using refresh cookie |
| POST | `/api/auth/logout` | Clears auth cookies |
| GET | `/api/auth/me` | Returns the current authenticated user |

## Expenses

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/expenses?page=&per_page=&month=&year=&category_id=&search=` | Paginated, filterable list |
| POST | `/api/expenses` | `{title, amount, category_id, notes, payment_method, expense_date}` |
| PUT | `/api/expenses/<id>` | Partial update, same fields |
| DELETE | `/api/expenses/<id>` | Delete |

## Income

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/income?page=&per_page=&month=&year=` | Paginated list |
| POST | `/api/income` | `{source, amount, category_id, notes, income_date}` |
| PUT | `/api/income/<id>` | Partial update |
| DELETE | `/api/income/<id>` | Delete |

## Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories?type=expense\|income` | List categories |
| POST | `/api/categories` | `{name, type, color, icon}` |
| DELETE | `/api/categories/<id>` | Delete (default categories are protected) |

## Budgets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/budgets?month=&year=` | List budgets for a period with computed spend |
| POST | `/api/budgets` | `{category_id, month, year, limit_amount}` (upserts existing) |
| DELETE | `/api/budgets/<id>` | Delete |

## Dashboard

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/summary?month=&year=` | Totals, category breakdown, 6-month trend, recent expenses, budget alerts |

## Reports

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports/export/csv?month=&year=` | Download CSV |
| GET | `/api/reports/export/pdf?month=&year=` | Download PDF |

## Uploads

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/uploads/receipt` | multipart `file` field → `{url}` |
| GET | `/api/uploads/receipt/<filename>` | Fetch an uploaded receipt |

## Admin (requires `role: admin`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/users` | List all users |
| PUT | `/api/admin/users/<id>/toggle-active` | Enable/disable a user |
| GET | `/api/admin/stats` | Platform-wide totals |
| GET | `/api/admin/audit-logs?page=&per_page=` | Paginated audit log |

## Error Format

```json
{ "error": "Human readable message", "details": { "field": ["reason"] } }
```
