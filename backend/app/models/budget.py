from datetime import datetime
from app.models.user import gen_uuid
from app.extensions import db


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        db.UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_period"),
    )

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id"), nullable=True)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    limit_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category")

    def to_dict(self, spent=0):
        limit = float(self.limit_amount)
        return {
            "id": self.id,
            "category": self.category.to_dict() if self.category else None,
            "month": self.month,
            "year": self.year,
            "limit_amount": limit,
            "spent": round(spent, 2),
            "remaining": round(limit - spent, 2),
            "percent_used": round((spent / limit) * 100, 1) if limit > 0 else 0,
        }
