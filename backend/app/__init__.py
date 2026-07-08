import os
from flask import Flask, jsonify
from app.config import config_map
from app.extensions import db, jwt, migrate, cors, bcrypt


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, supports_credentials=True, origins=app.config["CORS_ORIGINS"])

    from app.routes.auth import auth_bp
    from app.routes.expenses import expenses_bp
    from app.routes.income import income_bp
    from app.routes.categories import categories_bp
    from app.routes.budgets import budgets_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp
    from app.routes.uploads import uploads_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(pages_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "expense-tracker-api"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"error": "Authentication required"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"error": "Invalid or expired token"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Session expired, please log in again"}), 401

    return app


def repair_local_admin_access(app):
    from app.models import User

    with app.app_context():
        active_admin_count = User.query.filter_by(role="admin", is_active=True).count()
        if active_admin_count > 0:
            return False

        fallback_admin = User.query.filter_by(role="admin").order_by(User.created_at.asc()).first()
        if not fallback_admin:
            return False

        fallback_admin.is_active = True
        db.session.commit()
        app.logger.warning("Reactivated local admin account %s to restore access", fallback_admin.email)
        return True
