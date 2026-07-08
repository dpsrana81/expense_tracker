from flask import Blueprint, request, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import User, Expense, Income, AuditLog
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"items": [u.to_dict() for u in users]}), 200


@admin_bp.put("/users/<user_id>/toggle-active")
@admin_required
def toggle_active(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.is_active and user.role == "admin":
        active_admin_count = User.query.filter_by(role="admin", is_active=True).count()
        if active_admin_count <= 1:
            return jsonify({"error": "At least one active admin must remain enabled"}), 400

    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({"message": "User status updated", "user": user.to_dict()}), 200


@admin_bp.get("/stats")
@admin_required
def platform_stats():
    total_users = User.query.count()
    total_expenses = Expense.query.count()
    total_income_entries = Income.query.count()
    total_expense_amount = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()
    total_income_amount = db.session.query(func.coalesce(func.sum(Income.amount), 0)).scalar()

    return jsonify({
        "total_users": total_users,
        "total_expenses": total_expenses,
        "total_income_entries": total_income_entries,
        "total_expense_amount": float(total_expense_amount),
        "total_income_amount": float(total_income_amount),
    }), 200


@admin_bp.get("/audit-logs")
@admin_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [a.to_dict() for a in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
    }), 200
