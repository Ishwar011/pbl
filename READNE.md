
---

AI-Powered SAR Narrative Generator
Hack-O-Hire Submission | Compliance Automation System

---

Introduction

The AI-Powered Suspicious Activity Report (SAR) Narrative Generator is a compliance automation system designed to assist financial institutions in drafting structured, regulator-ready SAR narratives using a locally deployed Large Language Model (LLM).

Traditional SAR drafting is manual, time-consuming (5–6 hours per report), and subject to regulatory scrutiny. This system reduces drafting time to seconds while ensuring clarity, consistency, and auditability.

---

Problem Statement

Financial institutions are required to file Suspicious Activity Reports when potential money laundering or financial crime is detected. Current challenges include:

* Manual narrative drafting
* Inconsistent documentation quality
* Increasing regulatory scrutiny
* Compliance team workload and backlog
* Limited scalability

Poorly structured narratives may lead to remediation demands or enforcement actions.

---

Proposed Solution

The system introduces AI-assisted SAR narrative generation with:

* Local LLM-based text generation (Mistral)
* Structured prompt engineering
* FastAPI-based backend architecture
* Streamlit-based user interface
* Full audit trail logging

All processing is performed locally to ensure data privacy and security. No external API calls are required.

---

Key Features

* Automated SAR narrative generation
* Structured and regulator-ready formatting
* Consistent and transparent output
* Full input-output audit logging
* Modular and scalable architecture
* Secure local model inference

---

System Architecture

User Input (Streamlit UI)
→ FastAPI Backend
→ Prompt Engineering Layer
→ Local Mistral LLM
→ Structured SAR Narrative Output
→ Audit Logging

Components:

Frontend (Streamlit): Collects case and transaction details
Backend (FastAPI): Handles request processing and routing
Prompt Layer: Structures inputs for reliable AI output
LLM Layer: Generates narrative using local model
Logging Module: Stores input and output for audit traceability

---

Tech Stack

* Python 3.13
* FastAPI
* Streamlit
* Local Mistral LLM
* Uvicorn
* Pydantic

---

Project Structure

SAR-Generator/
│
├── app/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   └── models/
│
├── frontend/
│   └── streamlit_app.py
│
├── logs/
│
├── requirements.txt
└── README.md


Security Considerations

* No third-party API dependency
* Local model inference
* Environment variable-based secret handling
* Structured logging for compliance transparency

---

Impact

* Reduces SAR drafting time from 5–6 hours to seconds
* Improves narrative consistency and clarity
* Reduces compliance backlog
* Enables scalable regulatory reporting

---

Future Scope

* Integration with transaction monitoring systems
* Role-based access control
* Model explainability dashboard
* Containerized deployment
* Enterprise authentication layer

---

