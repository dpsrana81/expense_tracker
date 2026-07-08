from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    return render_template("login.html")


@pages_bp.get("/register")
def register_page():
    return render_template("register.html")


@pages_bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@pages_bp.get("/expenses")
def expenses_page():
    return render_template("expenses.html")


@pages_bp.get("/income")
def income_page():
    return render_template("income.html")


@pages_bp.get("/budgets")
def budgets_page():
    return render_template("budgets.html")


@pages_bp.get("/reports")
def reports_page():
    return render_template("reports.html")


@pages_bp.get("/admin")
def admin_page():
    return render_template("admin.html")
