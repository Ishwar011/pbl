from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database import models
from app.services.rule_engine import run_rules   # ✅ NEW IMPORT
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/cases", tags=["Cases"])


# -----------------------
# Database Dependency
# -----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------
# Pydantic Schemas
# -----------------------
class CaseCreate(BaseModel):
    customer_name: str
    risk_rating: str


class CaseResponse(BaseModel):
    id: int
    customer_name: str
    risk_rating: str
    status: str

    class Config:
        from_attributes = True


# -----------------------
# Create Case
# -----------------------
@router.post("/", response_model=CaseResponse)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    new_case = models.Case(
        customer_name=case.customer_name,
        risk_rating=case.risk_rating
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case


# -----------------------
# Get All Cases
# -----------------------
@router.get("/", response_model=List[CaseResponse])
def get_all_cases(db: Session = Depends(get_db)):
    return db.query(models.Case).all()

# -----------------------
# 🧱 STEP 1 — Get All Cases (Custom JSON Response)
# -----------------------
@router.get("/all")
def get_all_cases_custom(db: Session = Depends(get_db)):

    cases = db.query(models.Case).all()

    return [
        {
            "id": case.id,
            "customer_name": case.customer_name,
            "risk_rating": case.risk_rating,
            "status": case.status
        }
        for case in cases
    ]



# -----------------------
# Get Single Case
# -----------------------
@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


# -----------------------
# Delete Case
# -----------------------
@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    db.delete(case)
    db.commit()
    return {"message": "Case deleted successfully"}


# ==========================================================
# 🧠 STEP 4 – Run Rule Engine + Store in Audit Log
# ==========================================================
@router.post("/{case_id}/run-rules")
def execute_rules(case_id: int, db: Session = Depends(get_db)):

    # Check if case exists
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Run rule engine
    rules_triggered = run_rules(case_id, db)

    # Store triggered rules in AuditLog
    audit_entry = models.AuditLog(
        case_id=case_id,
        rules_triggered=str(rules_triggered),
        llm_prompt="",
        llm_output=""
    )

    db.add(audit_entry)
    db.commit()

    return {
        "case_id": case_id,
        "rules_triggered": rules_triggered
    }

# ==========================================================
# 🧱 STEP 2 — Total Transaction Volume per Case
# ==========================================================
@router.get("/{case_id}/summary")
def case_summary(case_id: int, db: Session = Depends(get_db)):

    # Check if case exists
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    transactions = db.query(models.Transaction)\
        .filter(models.Transaction.case_id == case_id)\
        .all()

    total_volume = sum(t.amount for t in transactions)
    transaction_count = len(transactions)

    return {
        "case_id": case_id,
        "total_volume": total_volume,
        "transaction_count": transaction_count
    }

# ==========================================================
# ➕ Add Transaction to Case
# ==========================================================
@router.post("/{case_id}/add-transaction")
def add_transaction(
    case_id: int,
    amount: float,
    sender: str,
    receiver_country: str,
    db: Session = Depends(get_db)
):

    # Check if case exists
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Create transaction
    transaction = models.Transaction(
        case_id=case_id,
        amount=amount,
        sender=sender,
        receiver_country=receiver_country
    )

    db.add(transaction)
    db.commit()

    return {"message": "Transaction added successfully"}
