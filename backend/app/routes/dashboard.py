from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import extract, func

from app.extensions import db
from app.models import Expense, Income, Category, Budget

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/summary")
@jwt_required()
def summary():
    uid = get_jwt_identity()
    today = date.today()
    month = request.args.get("month", type=int, default=today.month)
    year = request.args.get("year", type=int, default=today.year)

    total_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.user_id == uid,
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    ).scalar()

    total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(
        Income.user_id == uid,
        extract("month", Income.income_date) == month,
        extract("year", Income.income_date) == year,
    ).scalar()

    expense_count = Expense.query.filter(
        Expense.user_id == uid,
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    ).count()

    by_category = db.session.query(
        Category.name, Category.color, func.coalesce(func.sum(Expense.amount), 0)
    ).join(Expense, Expense.category_id == Category.id).filter(
        Expense.user_id == uid,
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    ).group_by(Category.id).order_by(func.sum(Expense.amount).desc()).all()

    category_breakdown = [
        {"name": name, "color": color, "amount": float(amount)} for name, color, amount in by_category
    ]

    # last 6 months trend
    trend = []
    for i in range(5, -1, -1):
        ref = (today.replace(day=1) - timedelta(days=1)) if False else None
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        exp = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == uid,
            extract("month", Expense.expense_date) == m,
            extract("year", Expense.expense_date) == y,
        ).scalar()
        inc = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(
            Income.user_id == uid,
            extract("month", Income.income_date) == m,
            extract("year", Income.income_date) == y,
        ).scalar()
        trend.append({
            "month": m, "year": y,
            "expense": float(exp), "income": float(inc),
        })

    recent_expenses = Expense.query.filter_by(user_id=uid).order_by(
        Expense.expense_date.desc(), Expense.created_at.desc()
    ).limit(5).all()

    budgets = Budget.query.filter_by(user_id=uid, month=month, year=year).all()
    budget_alerts = []
    for b in budgets:
        q = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == uid,
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year,
        )
        if b.category_id:
            q = q.filter(Expense.category_id == b.category_id)
        spent = float(q.scalar() or 0)
        limit = float(b.limit_amount)
        percent = round((spent / limit) * 100, 1) if limit > 0 else 0
        if percent >= 80:
            budget_alerts.append({
                "category": b.category.name if b.category else "Overall",
                "spent": spent, "limit": limit, "percent_used": percent,
            })

    return jsonify({
        "total_expense": float(total_expense),
        "total_income": float(total_income),
        "net_savings": float(total_income) - float(total_expense),
        "expense_count": expense_count,
        "category_breakdown": category_breakdown,
        "monthly_trend": trend,
        "recent_expenses": [e.to_dict() for e in recent_expenses],
        "budget_alerts": budget_alerts,
        "month": month,
        "year": year,
    }), 200
