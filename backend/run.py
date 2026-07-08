import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app import repair_local_admin_access
from app.extensions import db
from app.models import User, Category, Expense, Income, Budget, AuditLog

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db, "User": User, "Category": Category,
        "Expense": Expense, "Income": Income, "Budget": Budget, "AuditLog": AuditLog,
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        repair_local_admin_access(app)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
