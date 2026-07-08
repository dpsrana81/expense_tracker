from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import extract

from app.extensions import db
from app.models import Income
from app.models.audit_log import log_action
from app.schemas import IncomeSchema

income_bp = Blueprint("income", __name__, url_prefix="/api/income")
schema = IncomeSchema()


@income_bp.get("")
@jwt_required()
def list_income():
    uid = get_jwt_identity()
    q = Income.query.filter_by(user_id=uid)

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if month:
        q = q.filter(extract("month", Income.income_date) == month)
    if year:
        q = q.filter(extract("year", Income.income_date) == year)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = q.order_by(Income.income_date.desc(), Income.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [i.to_dict() for i in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
    }), 200


@income_bp.post("")
@jwt_required()
def create_income():
    uid = get_jwt_identity()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    income = Income(
        user_id=uid,
        source=data["source"].strip(),
        amount=data["amount"],
        category_id=data.get("category_id"),
        notes=data.get("notes"),
        income_date=data.get("income_date", date.today()),
    )
    db.session.add(income)
    db.session.commit()
    log_action(uid, "INCOME_CREATED", f"{income.source}: {income.amount}", request.remote_addr)
    return jsonify({"message": "Income added", "income": income.to_dict()}), 201


@income_bp.put("/<income_id>")
@jwt_required()
def update_income(income_id):
    uid = get_jwt_identity()
    income = Income.query.filter_by(id=income_id, user_id=uid).first()
    if not income:
        return jsonify({"error": "Income not found"}), 404
    try:
        data = schema.load(request.get_json(force=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    for field in ["source", "amount", "category_id", "notes", "income_date"]:
        if field in data:
            setattr(income, field, data[field])
    db.session.commit()
    log_action(uid, "INCOME_UPDATED", income.id, request.remote_addr)
    return jsonify({"message": "Income updated", "income": income.to_dict()}), 200


@income_bp.delete("/<income_id>")
@jwt_required()
def delete_income(income_id):
    uid = get_jwt_identity()
    income = Income.query.filter_by(id=income_id, user_id=uid).first()
    if not income:
        return jsonify({"error": "Income not found"}), 404
    db.session.delete(income)
    db.session.commit()
    log_action(uid, "INCOME_DELETED", income_id, request.remote_addr)
    return jsonify({"message": "Income deleted"}), 200
