import streamlit as st
import requests

import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


st.set_page_config(page_title="SAR Compliance System", layout="wide")

# =====================================================
# 🔐 SESSION STATE INIT
# =====================================================
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

# =====================================================
# 🔐 LOGIN SECTION
# =====================================================
if st.session_state.token is None:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={  # ✅ FIXED (was params before)
                    "username": username,
                    "password": password
                }
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error(response.json().get("detail", "Invalid credentials"))

        except Exception as e:
            st.error(f"Backend not reachable: {e}")

    st.stop()

# =====================================================
# 🔐 AUTH HEADER
# =====================================================
headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

# =====================================================
# MAIN UI
# =====================================================
st.title("🛡️ AI-Powered SAR Narrative Generator")
st.caption(f"Role: {st.session_state.role} | Regulatory-Compliant | Audit-Ready")

tabs = st.tabs(["📊 Dashboard", "📁 Case Management", "🧾 Narrative", "📜 Audit Trail"])

# =====================================================
# TAB 0 — DASHBOARD
# =====================================================
with tabs[0]:

    st.header("📊 Compliance Dashboard")

    response = requests.get(
        f"{BACKEND_URL}/cases/all",
        headers=headers
    )

    if response.status_code != 200:
        st.error("Unable to fetch cases")
    else:
        cases = response.json()

        if cases:
            st.subheader("📋 Case List")
            st.dataframe(cases, use_container_width=True)

            risk_counts = {}
            status_counts = {}

            for case in cases:
                risk_counts[case["risk_rating"]] = risk_counts.get(case["risk_rating"], 0) + 1
                status_counts[case["status"]] = status_counts.get(case["status"], 0) + 1

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Risk Distribution")
                st.bar_chart(risk_counts)

            with col2:
                st.subheader("Case Status Distribution")
                st.bar_chart(status_counts)
        else:
            st.info("No cases available yet.")

# =====================================================
# TAB 1 — CASE MANAGEMENT
# =====================================================
with tabs[1]:

    st.header("Create Case")

    col1, col2 = st.columns(2)

    with col1:
        customer_name = st.text_input("Customer Name")
    with col2:
        risk_rating = st.selectbox("Risk Rating", ["Low", "Medium", "High"])

    if st.button("Create Case"):
        response = requests.post(
            f"{BACKEND_URL}/cases/",
            json={
                "customer_name": customer_name,
                "risk_rating": risk_rating
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Case Created Successfully")
        else:
            st.error("Error creating case")

    st.divider()

    st.header("Add Transaction")

    col1, col2, col3 = st.columns(3)

    with col1:
        case_id_tx = st.number_input("Case ID", min_value=1, key="tx_case")
    with col2:
        amount = st.number_input("Amount", min_value=0.0)
    with col3:
        sender = st.text_input("Sender")

    country = st.text_input("Receiver Country")

    if st.button("Add Transaction"):
        response = requests.post(
            f"{BACKEND_URL}/cases/{case_id_tx}/add-transaction",
            params={
                "amount": amount,
                "sender": sender,
                "receiver_country": country
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Transaction Added Successfully")
        else:
            st.error("Error adding transaction")

# =====================================================
# TAB 2 — NARRATIVE
# =====================================================
with tabs[2]:

    st.header("Generate & Review SAR Narrative")

    case_id = st.number_input("Case ID", min_value=1, key="narr_case")

    if st.button("Generate Narrative"):
        response = requests.post(
            f"{BACKEND_URL}/narrative/{case_id}/generate",
            headers=headers
        )

        if response.status_code == 200:
            st.session_state["generated_data"] = response.json()
        else:
            st.error("Failed to generate narrative")

    if "generated_data" in st.session_state:

        data = st.session_state["generated_data"]

        st.subheader("📝 Narrative (Editable)")

        edited_text = st.text_area(
            "Edit Narrative Before Approval",
            value=data.get("sar_narrative", ""),
            height=400
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Save Edited Version"):
                response = requests.post(
                    f"{BACKEND_URL}/narrative/{case_id}/edit",
                    params={
                        "new_content": edited_text,
                        "editor_name": "Analyst_User"
                    },
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Edited Version Saved")
                else:
                    st.error("Edit failed")

        with col2:
            if st.button("Approve Narrative"):
                response = requests.post(
                    f"{BACKEND_URL}/narrative/{case_id}/approve",
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Narrative Approved")
                else:
                    st.error("You are not authorized to approve")

        with col3:
            if st.button("Download SAR PDF"):
                response = requests.get(
                    f"{BACKEND_URL}/narrative/{case_id}/export-pdf",
                    headers=headers
                )

                if response.status_code == 200:
                    st.download_button(
                        label="Click to Download",
                        data=response.content,
                        file_name=f"SAR_Case_{case_id}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Case must be approved before export.")

# =====================================================
# TAB 3 — AUDIT TRAIL
# =====================================================
with tabs[3]:

    st.header("Audit Trail Viewer")

    case_id_audit = st.number_input("Case ID", min_value=1, key="audit_case")

    if st.button("Load Audit Data"):
        response = requests.get(
            f"{BACKEND_URL}/narrative/{case_id_audit}/audit",
            headers=headers
        )

        if response.status_code == 200:
            audit_data = response.json()

            st.subheader("📋 Audit Logs")

            for log in audit_data["audit_logs"]:
                with st.expander(f"Audit Entry ID: {log['id']}"):
                    st.write("Rules Triggered:", log["rules_triggered"])
                    st.write("Retrieved Context:", log.get("retrieved_context"))
                    st.code(log["llm_prompt"])
                    st.code(log["llm_output"])

            st.subheader("Narrative Versions")

            for version in audit_data["narrative_versions"]:
                with st.expander(f"Version {version['version_number']} - {version['status']}"):
                    st.write("Edited By:", version["edited_by"])
                    st.write(version["content"])
        else:
            st.error("Failed to load audit data")
