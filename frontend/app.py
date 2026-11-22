# frontend/app.py
import sys, os
_sys_site = r"C:\Users\deepa\AppData\Local\Programs\Python\Python311\Lib\site-packages"
if os.path.exists(_sys_site) and _sys_site not in sys.path:
    sys.path.append(_sys_site)

import requests
import pandas as pd
import streamlit as st

API = "http://localhost:8000"
st.set_page_config(page_title="Failure Prediction AI", layout="wide")
st.title("Failure Prediction AI")
st.caption("Milestone 1: Data Collection & Market Intelligence")

tab_input, tab_history = st.tabs(["Project Input", "Past Projects"])

def show_analysis(p: dict):
    m = p.get("market_analysis")
    if not m:
        st.info("No analysis yet.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TAM", m["tam"]); c2.metric("SAM", m["sam"])
    c3.metric("SOM", m["som"]); c4.metric("Growth", m["growth_rate"])
    st.write(m["summary"])

    left, right = st.columns(2)
    with left:
        st.subheader("Market Trends")
        df = pd.DataFrame(m["trends"]).set_index("year")
        st.line_chart(df)
        st.markdown("**Opportunities**")
        for o in m["opportunities"]: st.write(f"- {o}")
        st.markdown("**Challenges**")
        for c in m["challenges"]: st.write(f"- {c}")
    with right:
        st.subheader("Competitor Landscape")
        st.dataframe(pd.DataFrame(p["competitors"]), hide_index=True)
    st.caption("Figures are AI-generated estimates. Verify before relying on them.")

with tab_input:
    with st.form("project_form"):
        name = st.text_input("Startup / Project Name", placeholder="e.g. TechVenture AI")
        c1, c2 = st.columns(2)
        ptype = c1.selectbox("Project Type", ["startup", "college_project", "hackathon", "business_plan"])
        industry = c2.selectbox("Industry", ["Technology", "Healthcare", "Education", "Finance", "E-commerce", "Other"])
        model = c1.selectbox("Business Model", ["SaaS", "Marketplace", "B2C", "B2B", "Non-profit", "Other"])
        budget = c2.number_input("Budget (USD)", min_value=1.0, value=100000.0, step=1000.0)
        market = st.text_input("Target Market", placeholder="e.g. SMBs in India")
        desc = st.text_area("Project Description", placeholder="Describe your idea (min 20 characters)")
        submitted = st.form_submit_button("Submit & Analyse")

    if submitted:
        payload = dict(project_name=name, project_type=ptype, industry=industry,
                       business_model=model, budget=budget, target_market=market, description=desc)
        try:
            r = requests.post(f"{API}/projects", json=payload, timeout=30)
            if r.status_code != 201:
                st.error(r.json())
            else:
                pid = r.json()["project_id"]
                st.success(f"Project #{pid} ('{name}') saved to PostgreSQL successfully!")
                with st.spinner("Analysing market and competitors..."):
                    a = requests.post(f"{API}/projects/{pid}/analyze", timeout=120)
                if a.ok:
                    show_analysis(a.json())
                else:
                    st.error(a.json().get("detail", "Analysis failed"))
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend API at http://127.0.0.1:8000. Please ensure the backend server is running.")

with tab_history:
    try:
        r = requests.get(f"{API}/projects", timeout=10)
        if r.status_code == 200:
            projects = r.json()
            if not projects:
                st.info("No projects recorded yet.")
            else:
                for p in projects:
                    with st.expander(f"#{p['project_id']} - {p['project_name']} ({p['project_type']}) - {p['industry']}"):
                        st.markdown(f"**Budget:** ${p['budget']:,.2f} | **Target Market:** {p['target_market']} | **Created:** {p['created_at']}")
                        st.markdown(f"**Description:** {p['description']}")
                        show_analysis(p)
        else:
            st.error(f"Failed to load projects: {r.text}")
    except Exception as e:
        st.warning(f"Could not connect to backend at {API}. Please ensure the FastAPI backend is running.")