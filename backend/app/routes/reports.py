import csv
import io
from datetime import date

from flask import Blueprint, request, jsonify, Response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import extract

from app.models import Expense, Income

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.get("/export/csv")
@jwt_required()
def export_csv():
    uid = get_jwt_identity()
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    q = Expense.query.filter_by(user_id=uid)
    if month:
        q = q.filter(extract("month", Expense.expense_date) == month)
    if year:
        q = q.filter(extract("year", Expense.expense_date) == year)
    expenses = q.order_by(Expense.expense_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Title", "Category", "Amount", "Payment Method", "Notes"])
    for e in expenses:
        writer.writerow([
            e.expense_date.isoformat() if e.expense_date else "",
            e.title,
            e.category.name if e.category else "Uncategorized",
            float(e.amount),
            e.payment_method or "",
            (e.notes or "").replace("\n", " "),
        ])

    output.seek(0)
    filename = f"expenses_{year or 'all'}_{month or 'all'}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@reports_bp.get("/export/pdf")
@jwt_required()
def export_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    uid = get_jwt_identity()
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    q = Expense.query.filter_by(user_id=uid)
    if month:
        q = q.filter(extract("month", Expense.expense_date) == month)
    if year:
        q = q.filter(extract("year", Expense.expense_date) == year)
    expenses = q.order_by(Expense.expense_date.desc()).all()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Expense Report", styles["Title"]), Spacer(1, 12)]

    data = [["Date", "Title", "Category", "Amount", "Payment"]]
    total = 0
    for e in expenses:
        data.append([
            e.expense_date.isoformat() if e.expense_date else "",
            e.title,
            e.category.name if e.category else "Uncategorized",
            f"{float(e.amount):.2f}",
            e.payment_method or "",
        ])
        total += float(e.amount)
    data.append(["", "", "", "", ""])
    data.append(["", "", "Total", f"{total:.2f}", ""])

    table = Table(data, colWidths=[2.5 * cm, 5 * cm, 4 * cm, 3 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.lightgrey),
        ("FONTNAME", (2, -1), (3, -1), "Helvetica-Bold"),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)

    filename = f"expense_report_{year or 'all'}_{month or 'all'}.pdf"
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=filename)
