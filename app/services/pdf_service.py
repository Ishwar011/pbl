from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from sqlalchemy.orm import Session
from app.database import models
from datetime import datetime
import os

def generate_sar_pdf(case_id: int, db: Session):

    case = db.query(models.Case).filter(models.Case.id == case_id).first()

    if case.status != "Approved":
        return None

    # Get latest approved narrative
    narrative = db.query(models.NarrativeVersion)\
        .filter(models.NarrativeVersion.case_id == case_id)\
        .order_by(models.NarrativeVersion.version_number.desc())\
        .first()

    # Get latest audit log
    audit = db.query(models.AuditLog)\
        .filter(models.AuditLog.case_id == case_id)\
        .order_by(models.AuditLog.id.desc())\
        .first()

    file_path = f"sar_report_case_{case_id}.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Suspicious Activity Report (SAR)", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Metadata Table
    metadata = Table([
        ["Case ID:", str(case_id)],
        ["Customer Name:", case.customer_name],
        ["Risk Rating:", case.risk_rating],
        ["Generated On:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ])

    metadata.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke)
    ]))

    elements.append(metadata)
    elements.append(Spacer(1, 0.4 * inch))

    # Rules Section
    elements.append(Paragraph("Triggered Rules:", styles["Heading2"]))

    rules = eval(audit.rules_triggered) if audit.rules_triggered else []

    rule_list = [ListItem(Paragraph(rule, styles["Normal"])) for rule in rules]
    elements.append(ListFlowable(rule_list, bulletType='bullet'))
    elements.append(Spacer(1, 0.4 * inch))

    # Regulatory Context
    elements.append(Paragraph("Regulatory Context:", styles["Heading2"]))
    elements.append(Paragraph(audit.retrieved_context or "N/A", styles["Normal"]))
    elements.append(Spacer(1, 0.4 * inch))

    # Final Narrative
    elements.append(Paragraph("Final Approved Narrative:", styles["Heading2"]))
    elements.append(Paragraph(narrative.content, styles["Normal"]))

    doc.build(elements)

    return file_path
