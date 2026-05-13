import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from app.database import models
from app.services.rag_service import retrieve_context

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY environment variable not set.")


def generate_sar_narrative(case_id: int, rules: list, db: Session):

    # Fetch case
    case = db.query(models.Case).filter(models.Case.id == case_id).first()

    # Fetch transactions
    transactions = db.query(models.Transaction).filter(
        models.Transaction.case_id == case_id
    ).all()

    # Build transaction summary
    transaction_summary = ""
    for t in transactions:
        transaction_summary += (
            f"Amount: {t.amount}, "
            f"Sender: {t.sender}, "
            f"Country: {t.receiver_country}\n"
        )

    # ==========================================================
    # 🚀 RAG Integration
    # ==========================================================
    rule_text = " ".join(rules)

    regulatory_context = retrieve_context(rule_text)

    context_text = "\n".join(regulatory_context)

    # ==========================================================
    # Build Enhanced Structured Prompt
    # ==========================================================
    prompt = f"""
You are a compliance officer AI generating a Suspicious Activity Report (SAR).

Use only provided facts.
Do not speculate.
Be unbiased and professional.

Regulatory Context:
{context_text}

Customer Name: {case.customer_name}
Risk Rating: {case.risk_rating}

Transactions:
{transaction_summary}

Rules Triggered:
{rules}

Generate structured SAR narrative with:
1. Introduction
2. Background
3. Transaction Analysis
4. Suspicion Rationale
5. Regulatory Reference
6. Conclusion
"""

    if not api_key:
        return prompt, "Error: GEMINI_API_KEY is not configured in the environment variables. Please set it in Render."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        output = response.text
    except Exception as e:
        output = f"Error generating narrative: {str(e)}"

    return prompt, output
