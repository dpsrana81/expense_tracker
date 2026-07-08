from datetime import datetime, date
from app.models.user import gen_uuid
from app.extensions import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id"), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(40), default="Cash")
    receipt_url = db.Column(db.String(255), nullable=True)
    expense_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": float(self.amount),
            "notes": self.notes,
            "payment_method": self.payment_method,
            "receipt_url": self.receipt_url,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "category": self.category.to_dict() if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
