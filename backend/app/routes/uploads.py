import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.utils.decorators import allowed_file

uploads_bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")


@uploads_bp.post("/receipt")
@jwt_required()
def upload_receipt():
    uid = get_jwt_identity()
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    if not allowed_file(file.filename, allowed):
        return jsonify({"error": f"File type not allowed. Allowed: {', '.join(allowed)}"}), 400

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{uid}_{uuid.uuid4().hex}.{ext}")
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # NOTE: When USE_S3 is enabled in config, this is where the file would be
    # uploaded to the configured Amazon S3 bucket instead of local disk, and
    # the resulting S3 object URL returned here.
    url = f"/api/uploads/receipt/{filename}"
    return jsonify({"message": "Receipt uploaded", "url": url}), 201


@uploads_bp.get("/receipt/<filename>")
@jwt_required()
def get_receipt(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
