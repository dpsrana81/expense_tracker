from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class ExpenseSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    amount = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0.01))
    category_id = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    payment_method = fields.String(allow_none=True)
    expense_date = fields.Date(allow_none=True)


class IncomeSchema(Schema):
    source = fields.String(required=True, validate=validate.Length(min=1, max=150))
    amount = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0.01))
    category_id = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    income_date = fields.Date(allow_none=True)


class CategorySchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=80))
    type = fields.String(required=True, validate=validate.OneOf(["expense", "income"]))
    color = fields.String(allow_none=True)
    icon = fields.String(allow_none=True)


class BudgetSchema(Schema):
    category_id = fields.String(allow_none=True)
    month = fields.Integer(required=True, validate=validate.Range(min=1, max=12))
    year = fields.Integer(required=True, validate=validate.Range(min=2000, max=2100))
    limit_amount = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0.01))
