from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
)
from marshmallow import ValidationError

from app.extensions import db
from app.models import User, Category, AuditLog
from app.models.category import DEFAULT_EXPENSE_CATEGORIES, DEFAULT_INCOME_CATEGORIES
from app.models.audit_log import log_action
from app.schemas import RegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()


def seed_default_categories(user_id):
    for name, color, icon in DEFAULT_EXPENSE_CATEGORIES:
        db.session.add(Category(user_id=user_id, name=name, type="expense",
                                 color=color, icon=icon, is_default=True))
    for name, color, icon in DEFAULT_INCOME_CATEGORIES:
        db.session.add(Category(user_id=user_id, name=name, type="income",
                                 color=color, icon=icon, is_default=True))
    db.session.commit()


@auth_bp.post("/register")
def register():
    try:
        data = register_schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    if User.query.filter_by(email=data["email"].lower()).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    is_first_user = User.query.count() == 0
    user = User(
        full_name=data["full_name"].strip(),
        email=data["email"].lower().strip(),
        role="admin" if is_first_user else "user",
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    seed_default_categories(user.id)
    log_action(user.id, "USER_REGISTERED", f"New account created for {user.email}", request.remote_addr)

    return jsonify({"message": "Account created successfully", "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    try:
        data = login_schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    user = User.query.filter_by(email=data["email"].lower().strip()).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "This account has been disabled"}), 403

    additional_claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.id, additional_claims=additional_claims)

    log_action(user.id, "USER_LOGIN", f"Login from {request.remote_addr}", request.remote_addr)

    resp = jsonify({"message": "Login successful", "user": user.to_dict()})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"error": "User not found"}), 404
    additional_claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    resp = jsonify({"message": "Token refreshed"})
    set_access_cookies(resp, access_token)
    return resp, 200


@auth_bp.post("/logout")
def logout():
    resp = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(resp)
    return resp, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200
