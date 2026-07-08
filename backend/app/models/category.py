from datetime import datetime
from app.models.user import gen_uuid
from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False, default="expense")  # expense | income
    color = db.Column(db.String(20), default="#6366f1")
    icon = db.Column(db.String(40), default="bi-tag")
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship("Expense", backref="category", lazy=True)
    incomes = db.relationship("Income", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "color": self.color,
            "icon": self.icon,
            "is_default": self.is_default,
        }


DEFAULT_EXPENSE_CATEGORIES = [
    ("Food & Dining", "#f59e0b", "bi-cup-hot"),
    ("Transportation", "#3b82f6", "bi-car-front"),
    ("Housing & Rent", "#8b5cf6", "bi-house-door"),
    ("Utilities", "#06b6d4", "bi-lightning-charge"),
    ("Healthcare", "#ef4444", "bi-heart-pulse"),
    ("Entertainment", "#ec4899", "bi-controller"),
    ("Shopping", "#10b981", "bi-bag"),
    ("Education", "#6366f1", "bi-mortarboard"),
    ("Travel", "#14b8a6", "bi-airplane"),
    ("Other", "#64748b", "bi-three-dots"),
]

DEFAULT_INCOME_CATEGORIES = [
    ("Salary", "#10b981", "bi-cash-stack"),
    ("Freelance", "#3b82f6", "bi-briefcase"),
    ("Investments", "#8b5cf6", "bi-graph-up-arrow"),
    ("Gifts", "#ec4899", "bi-gift"),
    ("Other Income", "#64748b", "bi-three-dots"),
]
