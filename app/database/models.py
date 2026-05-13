from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    risk_rating = Column(String, nullable=False)
    status = Column(String, default="Draft")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transactions = relationship(
        "Transaction",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    narrative_versions = relationship(
        "NarrativeVersion",
        back_populates="case",
        cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)
    sender = Column(String, nullable=False)
    receiver_country = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="transactions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"))

    rules_triggered = Column(Text)
    retrieved_context = Column(Text)   # ✅ NEW COLUMN (RAG Context Stored)
    llm_prompt = Column(Text)
    llm_output = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="audit_logs")


# ==========================================================
# 📄 Narrative Version Table
# ==========================================================
class NarrativeVersion(Base):
    __tablename__ = "narrative_versions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"))
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    edited_by = Column(String)
    status = Column(String)  # Draft / Edited / Approved

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="narrative_versions")

# ==========================================================
# 👤 User Table (Authentication & Roles)
# ==========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(String, nullable=False)  # Analyst / Officer / Admin

    created_at = Column(DateTime(timezone=True), server_default=func.now())
