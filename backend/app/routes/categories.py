from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models import Category
from app.schemas import CategorySchema

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")
schema = CategorySchema()


@categories_bp.get("")
@jwt_required()
def list_categories():
    uid = get_jwt_identity()
    type_filter = request.args.get("type")
    q = Category.query.filter_by(user_id=uid)
    if type_filter:
        q = q.filter_by(type=type_filter)
    categories = q.order_by(Category.name).all()
    return jsonify({"items": [c.to_dict() for c in categories]}), 200


@categories_bp.post("")
@jwt_required()
def create_category():
    uid = get_jwt_identity()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    category = Category(
        user_id=uid,
        name=data["name"].strip(),
        type=data["type"],
        color=data.get("color", "#6366f1"),
        icon=data.get("icon", "bi-tag"),
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({"message": "Category created", "category": category.to_dict()}), 201


@categories_bp.delete("/<category_id>")
@jwt_required()
def delete_category(category_id):
    uid = get_jwt_identity()
    category = Category.query.filter_by(id=category_id, user_id=uid).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404
    if category.is_default:
        return jsonify({"error": "Default categories cannot be deleted"}), 400
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200
