from sqlalchemy.orm import Session
from app.database import models

def run_rules(case_id: int, db: Session):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.case_id == case_id
    ).all()

    rules_triggered = []

    # Rule 1: Large Total Incoming Amount
    total_amount = sum(t.amount for t in transactions)

    if total_amount > 5000000:
        rules_triggered.append("High total transaction volume detected")

    # Rule 2: Many unique senders
    unique_senders = len(set(t.sender for t in transactions))

    if unique_senders > 10:
        rules_triggered.append("Structuring pattern - many unique senders")

    # Rule 3: Foreign transfers
    foreign_transfers = [
        t for t in transactions if t.receiver_country.lower() != "india"
    ]

    if len(foreign_transfers) > 0:
        rules_triggered.append("Foreign transfer detected")

    return rules_triggered
