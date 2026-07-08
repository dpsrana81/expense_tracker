from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import extract, func

from app.extensions import db
from app.models import Budget, Expense
from app.schemas import BudgetSchema

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")
schema = BudgetSchema()


def calc_spent(uid, category_id, month, year):
    q = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.user_id == uid,
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    )
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    return float(q.scalar() or 0)


@budgets_bp.get("")
@jwt_required()
def list_budgets():
    uid = get_jwt_identity()
    month = request.args.get("month", type=int, default=date.today().month)
    year = request.args.get("year", type=int, default=date.today().year)

    budgets = Budget.query.filter_by(user_id=uid, month=month, year=year).all()
    result = []
    for b in budgets:
        spent = calc_spent(uid, b.category_id, month, year)
        result.append(b.to_dict(spent=spent))
    return jsonify({"items": result, "month": month, "year": year}), 200


@budgets_bp.post("")
@jwt_required()
def create_budget():
    uid = get_jwt_identity()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    existing = Budget.query.filter_by(
        user_id=uid, category_id=data.get("category_id"),
        month=data["month"], year=data["year"]
    ).first()
    if existing:
        existing.limit_amount = data["limit_amount"]
        db.session.commit()
        spent = calc_spent(uid, existing.category_id, existing.month, existing.year)
        return jsonify({"message": "Budget updated", "budget": existing.to_dict(spent=spent)}), 200

    budget = Budget(
        user_id=uid,
        category_id=data.get("category_id"),
        month=data["month"],
        year=data["year"],
        limit_amount=data["limit_amount"],
    )
    db.session.add(budget)
    db.session.commit()
    spent = calc_spent(uid, budget.category_id, budget.month, budget.year)
    return jsonify({"message": "Budget created", "budget": budget.to_dict(spent=spent)}), 201


@budgets_bp.delete("/<budget_id>")
@jwt_required()
def delete_budget(budget_id):
    uid = get_jwt_identity()
    budget = Budget.query.filter_by(id=budget_id, user_id=uid).first()
    if not budget:
        return jsonify({"error": "Budget not found"}), 404
    db.session.delete(budget)
    db.session.commit()
    return jsonify({"message": "Budget deleted"}), 200
