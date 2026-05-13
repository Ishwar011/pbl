from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database import models
from app.services.rule_engine import run_rules
from app.services.llm_service import generate_sar_narrative
from app.services.rbac_service import require_role
from app.services.pdf_service import generate_sar_pdf

router = APIRouter(prefix="/narrative", tags=["Narrative"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================================
# ✅ GENERATE NARRATIVE (FIXED VERSION)
# ==========================================================
@router.post("/{case_id}/generate")
def generate_narrative(case_id: int, db: Session = Depends(get_db)):

    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Run rules
    rules = run_rules(case_id, db)

    # Generate LLM Narrative
    prompt, output = generate_sar_narrative(case_id, rules, db)

    # Save audit log
    audit_entry = models.AuditLog(
        case_id=case_id,
        rules_triggered=str(rules),
        llm_prompt=prompt,
        llm_output=output
    )
    db.add(audit_entry)

    # Check previous versions
    latest = db.query(models.NarrativeVersion) \
        .filter(models.NarrativeVersion.case_id == case_id) \
        .order_by(models.NarrativeVersion.version_number.desc()) \
        .first()

    new_version_number = 1 if not latest else latest.version_number + 1

    # Save narrative version
    version = models.NarrativeVersion(
        case_id=case_id,
        version_number=new_version_number,
        content=output,
        edited_by="AI",
        status="Draft"
    )
    db.add(version)

    db.commit()

    # ✅ RETURN NARRATIVE TEXT
    return {
        "message": "Narrative Generated",
        "case_id": case_id,
        "version": new_version_number,
        "status": "Draft",
        "sar_narrative": output
    }


# ==========================================================
# EDIT NARRATIVE
# ==========================================================
@router.post("/{case_id}/edit")
def edit_narrative(
    case_id: int,
    new_content: str,
    editor_name: str,
    db: Session = Depends(get_db)
):

    latest = db.query(models.NarrativeVersion) \
        .filter(models.NarrativeVersion.case_id == case_id) \
        .order_by(models.NarrativeVersion.version_number.desc()) \
        .first()

    if not latest:
        raise HTTPException(status_code=404, detail="No narrative found")

    new_version_number = latest.version_number + 1

    edited_version = models.NarrativeVersion(
        case_id=case_id,
        version_number=new_version_number,
        content=new_content,
        edited_by=editor_name,
        status="Edited"
    )

    db.add(edited_version)
    db.commit()

    return {
        "message": "Narrative Edited",
        "version": new_version_number
    }


# ==========================================================
# APPROVE NARRATIVE
# ==========================================================
@router.post("/{case_id}/approve")
def approve_narrative(
    case_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("Officer"))
):

    latest = db.query(models.NarrativeVersion) \
        .filter(models.NarrativeVersion.case_id == case_id) \
        .order_by(models.NarrativeVersion.version_number.desc()) \
        .first()

    if not latest:
        raise HTTPException(status_code=404, detail="No narrative found")

    latest.status = "Approved"

    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if case:
        case.status = "Approved"

    db.commit()

    return {
        "message": "Narrative Approved",
        "approved_by": user["sub"]
    }


# ==========================================================
# EXPORT PDF
# ==========================================================
@router.get("/{case_id}/export-pdf")
def export_pdf(case_id: int, db: Session = Depends(get_db)):

    file_path = generate_sar_pdf(case_id, db)

    if not file_path:
        raise HTTPException(status_code=400, detail="Case not approved yet")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"SAR_Case_{case_id}.pdf"
    )


# ==========================================================
# VIEW AUDIT TRAIL
# ==========================================================
@router.get("/{case_id}/audit")
def view_audit(case_id: int, db: Session = Depends(get_db)):

    audits = db.query(models.AuditLog) \
        .filter(models.AuditLog.case_id == case_id) \
        .all()

    versions = db.query(models.NarrativeVersion) \
        .filter(models.NarrativeVersion.case_id == case_id) \
        .all()

    return {
        "audit_logs": audits,
        "narrative_versions": versions
    }
