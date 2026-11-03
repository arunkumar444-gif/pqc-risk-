import json
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from core.database import (
    init_db, insert_asset, get_all_assets, clear_all_data, 
    verify_user, register_user, get_connection, DB_PATH
)
from core.extractor import extract_from_pdf_stream, extract_from_csv, extract_from_json
from core.risk_engine import calculate_quantum_risk
from core.readiness_engine import calculate_pqc_readiness
from core.agility_engine import calculate_agility_score
from core.migration_engine import generate_recommendation_and_priority

st.set_page_config(
    page_title="PQC Risk Analyzer & Migration Engine",
    page_icon="⚛️",
    layout="wide"
)

init_db()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "preferred_lang" not in st.session_state:
    st.session_state.preferred_lang = "English"

# Quantum Cyber Visual Theme CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #0B0E14; color: #E0E6ED; }
    .stSidebar { background-color: #121721; border-right: 1px solid #1F2937; }
    
    .quantum-card {
        background: linear-gradient(135deg, #131B2E 0%, #0B0E14 100%);
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 242, 254, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    
    .quantum-glow {
        color: #00F2FE;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# AUTHENTICATION GATEKEEPER (SIGN IN & CREATE ACCOUNT)
# -------------------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;' class='quantum-glow'>⚛️ POST-QUANTUM RISK ANALYZER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>Enterprise Quantum Cryptographic Assessment & Migration Platform</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio("Select Action", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "Sign In":
            st.markdown("""
            <div class="quantum-card">
                <h3 class="quantum-glow">Analyst Sign In</h3>
                <p style="font-size: 0.9em; color: #64748B;">Enter your credentials to access the quantum risk engine</p>
            </div>
            """, unsafe_allow_html=True)
            
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            login_lang = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Japanese"], key="login_lang")
            
            if st.button("🔐 Sign In", use_container_width=True):
                user_rec = verify_user(login_user, login_pass)
                if user_rec:
                    st.session_state.authenticated = True
                    st.session_state.username = user_rec['username']
                    st.session_state.preferred_lang = login_lang
                    st.success(f"Welcome back, {user_rec['username']}! Signed in successfully.")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. (Default credentials: admin / admin123)")
            
            st.caption("💡 Default Admin Credentials: Username: **admin** | Password: **admin123**")
            
        else:
            st.markdown("""
            <div class="quantum-card">
                <h3 class="quantum-glow">Create Account</h3>
                <p style="font-size: 0.9em; color: #64748B;">Create a new cryptographic analyst profile</p>
            </div>
            """, unsafe_allow_html=True)
            
            new_user = st.text_input("Choose Username", key="new_user")
            new_pass = st.text_input("Choose Password", type="password", key="new_pass")
            new_lang = st.selectbox("Select Preferred Language", ["English", "Spanish", "French", "German", "Japanese"], key="new_lang")
            
            if st.button("📝 Create Account", use_container_width=True):
                if new_user.strip() and new_pass.strip():
                    success = register_user(new_user, new_pass, role="Analyst", language=new_lang)
                    if success:
                        st.success("Account created successfully! Switch to 'Sign In' above to log in.")
                    else:
                        st.error("Username already exists. Please choose a different username.")
                else:
                    st.warning("Please fill in both username and password fields.")
                    
    st.stop()

# -------------------------------------------------------------------
# AUTHENTICATED SIDEBAR NAVIGATION
# -------------------------------------------------------------------
st.sidebar.markdown(f"👤 **User:** `{st.session_state.username}`")
st.sidebar.markdown(f"🌐 **Language:** `{st.session_state.preferred_lang}`")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.title("⚛️ PQC Risk Analyzer")
st.sidebar.caption("Cryptographic Agility Engine")

nav = st.sidebar.radio(
    "Navigation",
    [
        "1. Home / Welcome",
        "2. Dashboard",
        "3. Upload PDF / CSV / JSON",
        "4. Cryptographic Asset Discovery",
        "5. Quantum Risk Assessment",
        "6. PQC Readiness Assessment",
        "7. Cryptographic Agility Analysis",
        "8. Migration Prioritization",
        "9. Recommendations",
        "10. Reports & History",
        "11. Settings / About"
    ]
)

# -------------------------------------------------------------------
# PAGE 1: HOME
# -------------------------------------------------------------------
if nav == "1. Home / Welcome":
    st.title("Post-Quantum Communication Risk Analyzer")
    st.subheader("Cryptographic Agility and Migration Prioritization Framework")
    
    st.markdown("""
    <div class="quantum-card">
        <h2 class="quantum-glow">Quantum Threat Landscape Overview</h2>
        <p>Shor's algorithm executed on Cryptographically Relevant Quantum Computers (CRQCs) will break RSA, ECC, and Diffie-Hellman ciphers. This system audits enterprise infrastructure to prepare for NIST FIPS 203, 204, and 205 post-quantum standards.</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# PAGE 2: DASHBOARD
# -------------------------------------------------------------------
elif nav == "2. Dashboard":
    st.title("Operational Risk & Migration Dashboard")
    assets = get_all_assets()
    
    if not assets:
        st.warning("No cryptographic assets analyzed yet. Use the Upload or Manual Entry views to populate data.")
    else:
        df = pd.DataFrame(assets)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Assets", len(df))
        c2.metric("Critical Risk", len(df[df['risk_category'] == 'CRITICAL']))
        c3.metric("High Risk", len(df[df['risk_category'] == 'HIGH']))
        c4.metric("Avg Risk Score", round(df['overall_risk_score'].mean(), 1))
        c5.metric("Avg Agility Score", round(df['agility_score'].mean(), 1))
        
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(df, names='risk_category', title="Risk Category Distribution", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.histogram(df, x='priority_code', color='priority_code', title="Migration Priority Tiers",
                                color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig2, use_container_width=True)
            
        st.markdown("---")
        st.subheader("📊 Quantum Risk vs. Cryptographic Agility Matrix")
        fig3 = px.scatter(
            df,
            x="agility_score",
            y="overall_risk_score",
            color="priority_code",
            size="exposure_score",
            hover_name="asset_name",
            hover_data=["algorithm_name", "recommended_standard"],
            title="Asset Distribution: Risk Score vs. Agility Score",
            labels={"agility_score": "Cryptographic Agility Score", "overall_risk_score": "Quantum Risk Score ($R$)"},
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------------------------
# PAGE 3: UPLOAD & EXTRACTION
# -------------------------------------------------------------------
elif nav == "3. Upload PDF / CSV / JSON":
    st.title("Input Processing & Cryptographic Extraction")
    
    upload_type = st.selectbox("Select Input File Type", ["PDF Document", "CSV Manifest", "JSON File"])
    uploaded_file = st.file_uploader("Choose a file to analyze", type=["pdf", "csv", "json"])
    
    if uploaded_file:
        records = []
        msg = "File parsed successfully."
        file_ext = uploaded_file.name.split(".")[-1].lower()
        
        if upload_type == "PDF Document" and file_ext == "pdf":
            records, msg = extract_from_pdf_stream(uploaded_file.read())
        elif upload_type == "CSV Manifest" and file_ext == "csv":
            records = extract_from_csv(uploaded_file)
        elif upload_type == "JSON File" and file_ext == "json":
            records = extract_from_json(uploaded_file)
        else:
            st.error(f"Selected input type '{upload_type}' does not match uploaded file extension '.{file_ext}'!")

        if records:
            st.info(msg)
            st.subheader("Extracted Configurations & Auto-Calculated Scores")
            df_review = pd.DataFrame(records)
            st.dataframe(df_review, use_container_width=True)
            
            if st.button("Confirm and Process Extracted Assets"):
                for r in records:
                    r_score, r_cat = calculate_quantum_risk(
                        r['exposure'], r['sensitivity'], r['lifetime'], r['external'], r['criticality']
                    )
                    rec, rat, prio = generate_recommendation_and_priority(
                        r['algorithm_name'], r['cryptographic_purpose'], r_score, int(r['lifetime'])
                    )
                    
                    full_record = {
                        "asset_name": r['asset_name'],
                        "environment": r['environment'],
                        "algorithm_name": r['algorithm_name'],
                        "algorithm_category": r['algorithm_category'],
                        "key_size": r['key_size'],
                        "cryptographic_purpose": r['cryptographic_purpose'],
                        "provenance": r['provenance'],
                        "exposure_score": r['exposure'],
                        "sensitivity_score": r['sensitivity'],
                        "lifetime_score": r['lifetime'],
                        "external_score": r['external'],
                        "criticality_score": r['criticality'],
                        "overall_risk_score": r_score,
                        "risk_category": r_cat,
                        "readiness_score": r['readiness'],
                        "agility_score": r['agility'],
                        "priority_code": prio,
                        "recommended_standard": rec,
                        "rationale": rat
                    }
                    insert_asset(full_record)
                st.success("Assets successfully saved to database! View Dashboard for updated visualizations.")

# -------------------------------------------------------------------
# PAGE 4: ASSET DISCOVERY
# -------------------------------------------------------------------
elif nav == "4. Cryptographic Asset Discovery":
    st.title("Cryptographic Asset Inventory")
    assets = get_all_assets()
    if assets:
        st.dataframe(pd.DataFrame(assets)[['id', 'asset_name', 'environment', 'algorithm_name', 'key_size', 'cryptographic_purpose']], use_container_width=True)
    else:
        st.info("No assets registered yet.")

# -------------------------------------------------------------------
# PAGE 5: QUANTUM RISK ASSESSMENT
# -------------------------------------------------------------------
elif nav == "5. Quantum Risk Assessment":
    st.title("Quantum Risk Assessment Engine")
    c = st.slider("Cryptographic Exposure (C)", 0, 5, 4)
    s = st.slider("Data Sensitivity (S)", 0, 5, 5)
    l = st.slider("Confidentiality Lifetime (L)", 0, 5, 5)
    e = st.slider("External Exposure (E)", 0, 5, 4)
    b = st.slider("Business Criticality (B)", 0, 5, 4)
    score, category = calculate_quantum_risk(c, s, l, e, b)
    st.metric("Computed Quantum Risk Score", f"{score} / 100", delta=category, delta_color="inverse")

# -------------------------------------------------------------------
# PAGE 6: PQC READINESS
# -------------------------------------------------------------------
elif nav == "6. PQC Readiness Assessment":
    st.title("PQC Readiness Assessment")
    inv = st.slider("Inventory Completeness (%)", 0, 100, 70)
    aw = st.slider("Standard Awareness (%)", 0, 100, 50)
    lib = st.slider("Library Compatibility (%)", 0, 100, 30)
    hyb = st.slider("Hybrid Evaluation (%)", 0, 100, 20)
    test = st.slider("Testing (%)", 0, 100, 10)
    gov = st.slider("Governance (%)", 0, 100, 40)
    readiness = calculate_pqc_readiness(inv, aw, lib, hyb, test, gov)
    st.metric("Overall PQC Readiness Rating", f"{readiness}%")

# -------------------------------------------------------------------
# PAGE 7: AGILITY ANALYSIS
# -------------------------------------------------------------------
elif nav == "7. Cryptographic Agility Analysis":
    st.title("Cryptographic Agility Analyzer")
    a1 = st.slider("Absence of Hardcoded Primitives (0-5)", 0, 5, 2)
    a2 = st.slider("Modular Architecture (0-5)", 0, 5, 3)
    a3 = st.slider("Centralized Configuration (0-5)", 0, 5, 2)
    a4 = st.slider("Dependency Docs (0-5)", 0, 5, 3)
    a5 = st.slider("Key Management Adaptability (0-5)", 0, 5, 2)
    a6 = st.slider("Automated Validation (0-5)", 0, 5, 1)
    agility = calculate_agility_score(a1, a2, a3, a4, a5, a6)
    st.metric("Cryptographic Agility Score", f"{agility} / 100")

# -------------------------------------------------------------------
# PAGE 8: MIGRATION PRIORITIZATION
# -------------------------------------------------------------------
elif nav == "8. Migration Prioritization":
    st.title("Migration Prioritization Matrix")
    assets = get_all_assets()
    if assets:
        st.dataframe(pd.DataFrame(assets)[['asset_name', 'algorithm_name', 'overall_risk_score', 'priority_code', 'recommended_standard']], use_container_width=True)
    else:
        st.info("No prioritized assets available.")

# -------------------------------------------------------------------
# PAGE 9: RECOMMENDATIONS
# -------------------------------------------------------------------
elif nav == "9. Recommendations":
    st.title("NIST PQC Migration Roadmap")
    st.markdown("""
    - **FIPS 203 (ML-KEM)**: Key encapsulation mechanism for encryption and key exchange.
    - **FIPS 204 (ML-DSA)**: Digital signature algorithm for PKI and authentication.
    - **FIPS 205 (SLH-DSA)**: Stateless hash-based signatures as an algorithmic backup.
    """)

# -------------------------------------------------------------------
# PAGE 10: REPORTS & HISTORY
# -------------------------------------------------------------------
elif nav == "10. Reports & History":
    st.title("Reports & Export History")
    assets = get_all_assets()
    if assets:
        df = pd.DataFrame(assets)
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Assessment Ledger (CSV)", data=csv, file_name="pqc_assessment_report.csv", mime="text/csv", use_container_width=True)
        with col2:
            json_data = json.dumps(assets, indent=2)
            st.download_button("📥 Export Cryptographic Ledger (JSON)", data=json_data, file_name="pqc_assessment_report.json", mime="application/json", use_container_width=True)
    else:
        st.info("No history available.")

# -------------------------------------------------------------------
# PAGE 11: SETTINGS / ABOUT (EXPANDED SYSTEM OPTIONS & DETAILS)
# -------------------------------------------------------------------
elif nav == "11. Settings / About":
    st.title("Settings & Platform Management")
    st.caption("Manage system options, account preferences, database health, and PQC compliance standards.")
    
    # Section 1: Active User & Account Details
    st.subheader("👤 User Profile & Session Details")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, signup_time, preferred_language FROM users WHERE username = ?", (st.session_state.username,))
    user_info = cursor.fetchone()
    conn.close()
    
    u_role = user_info['role'] if user_info else "Analyst"
    u_signup = user_info['signup_time'] if (user_info and user_info['signup_time']) else "N/A (System Account)"
    u_lang = st.session_state.preferred_lang
    
    col_u1, col_u2, col_u3 = st.columns(3)
    col_u1.metric("Active Username", st.session_state.username)
    col_u2.metric("Assigned Role", u_role)
    col_u3.metric("Account Created On", u_signup)
    
    st.markdown("---")
    
    # Section 2: Database Health & System Metrics
    st.subheader("🛠️ System Health & Storage Statistics")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM assets")
    asset_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    conn.close()
    
    db_size = round(Path(DB_PATH).stat().st_size / 1024, 2) if Path(DB_PATH).exists() else 0.0
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Database Status", "Connected (SQLite)")
    col_s2.metric("Stored Assets", f"{asset_count} Records")
    col_s3.metric("Registered Users", f"{user_count} Users")
    col_s4.metric("Database File Size", f"{db_size} KB")
    
    st.caption(f"📁 Database Location: `{DB_PATH}`")
    
    st.markdown("---")
    
    # Section 3: Database Administration Options
    st.subheader("⚠️ Database Maintenance Controls")
    st.write("Perform administrative database cleanup operations.")
    
    if st.button("🗑️ Clear All Asset Ledger Records", type="secondary"):
        clear_all_data()
        st.success("All cryptographic asset records have been successfully purged from the database!")
        st.rerun()

    st.markdown("---")
    
    # Section 4: About Post-Quantum Communication Risk Analyzer
    st.subheader("ℹ️ About the Framework")
    st.markdown("""
    **Post-Quantum Communication Risk Analyzer** is an enterprise cybersecurity framework engineered to audit, score, and prioritize classical cryptographic assets for transition to post-quantum security standards.
    
    - **Engine Version**: `v2.4.0 (NIST FIPS Aligned)`
    - **Quantum Cryptanalysis Basis**: Evaluates Shor's Algorithm (integer factorization & ECDLP collapse) and Grover's Search (symmetric key halving).
    - **Harvest Now, Decrypt Later (HNDL)**: Automatically factors in data confidentiality lifetimes to prioritize vulnerable long-retention assets.
    - **Standard Compliance**:
      - **NIST FIPS 203 (ML-KEM)**: Module-Lattice-Based Key-Encapsulation Mechanism.
      - **NIST FIPS 204 (ML-DSA)**: Module-Lattice-Based Digital Signature Standard.
      - **NIST FIPS 205 (SLH-DSA)**: Stateless Hash-Based Digital Signature Standard.
    """)
    