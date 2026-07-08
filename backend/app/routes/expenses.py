from datetime import date, datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import extract

from app.extensions import db
from app.models import Expense, Category
from app.models.audit_log import log_action
from app.schemas import ExpenseSchema

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")
schema = ExpenseSchema()


@expenses_bp.get("")
@jwt_required()
def list_expenses():
    uid = get_jwt_identity()
    q = Expense.query.filter_by(user_id=uid)

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    category_id = request.args.get("category_id")
    search = request.args.get("search")

    if month:
        q = q.filter(extract("month", Expense.expense_date) == month)
    if year:
        q = q.filter(extract("year", Expense.expense_date) == year)
    if category_id:
        q = q.filter_by(category_id=category_id)
    if search:
        q = q.filter(Expense.title.ilike(f"%{search}%"))

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = q.order_by(Expense.expense_date.desc(), Expense.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "items": [e.to_dict() for e in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
    }), 200


@expenses_bp.post("")
@jwt_required()
def create_expense():
    uid = get_jwt_identity()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    expense = Expense(
        user_id=uid,
        title=data["title"].strip(),
        amount=data["amount"],
        category_id=data.get("category_id"),
        notes=data.get("notes"),
        payment_method=data.get("payment_method", "Cash"),
        expense_date=data.get("expense_date", date.today()),
    )
    db.session.add(expense)
    db.session.commit()
    log_action(uid, "EXPENSE_CREATED", f"{expense.title}: {expense.amount}", request.remote_addr)
    return jsonify({"message": "Expense added", "expense": expense.to_dict()}), 201


@expenses_bp.put("/<expense_id>")
@jwt_required()
def update_expense(expense_id):
    uid = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=uid).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    try:
        data = schema.load(request.get_json(force=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    for field in ["title", "amount", "category_id", "notes", "payment_method", "expense_date"]:
        if field in data:
            setattr(expense, field, data[field])
    db.session.commit()
    log_action(uid, "EXPENSE_UPDATED", expense.id, request.remote_addr)
    return jsonify({"message": "Expense updated", "expense": expense.to_dict()}), 200


@expenses_bp.delete("/<expense_id>")
@jwt_required()
def delete_expense(expense_id):
    uid = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=uid).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    db.session.delete(expense)
    db.session.commit()
    log_action(uid, "EXPENSE_DELETED", expense_id, request.remote_addr)
    return jsonify({"message": "Expense deleted"}), 200
