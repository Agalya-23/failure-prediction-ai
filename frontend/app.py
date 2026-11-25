# frontend/app.py
import requests
import pandas as pd
import streamlit as st

API = "http://localhost:8000"
st.set_page_config(page_title="Failure Prediction AI", layout="wide")

# Custom CSS for modern dashboard styling
st.markdown("""
<style>
    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .risk-score-display {
        font-size: 56px;
        font-weight: 800;
        line-height: 1.1;
        text-align: center;
        margin: 10px 0;
    }
    .risk-badge {
        font-size: 13px;
        font-weight: 700;
        text-align: center;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .swot-card {
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        min-height: 190px;
    }
    .swot-strengths {
        background: rgba(46, 125, 50, 0.12);
        border-left: 4px solid #4caf50;
    }
    .swot-weaknesses {
        background: rgba(211, 47, 47, 0.12);
        border-left: 4px solid #f44336;
    }
    .swot-opportunities {
        background: rgba(25, 118, 210, 0.12);
        border-left: 4px solid #2196f3;
    }
    .swot-threats {
        background: rgba(230, 81, 0, 0.12);
        border-left: 4px solid #ff9800;
    }
    .swot-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .feasibility-box {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        border-left: 3px solid #26a69a;
    }
</style>
""", unsafe_allow_html=True)

st.title("Failure Prediction AI")
st.caption("AI-Powered Startup Risk Scoring, Market Intelligence & Strategic Evaluation")

tab_input, tab_strategic, tab_history = st.tabs([
    "📝 Project Input",
    "🎯 Risk, SWOT & Feasibility",
    "🗂️ Past Projects"
])


def show_market_analysis(p: dict):
    m = p.get("market_analysis")
    if not m:
        st.info("No market analysis recorded yet.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TAM", m.get("tam", "N/A"))
    c2.metric("SAM", m.get("sam", "N/A"))
    c3.metric("SOM", m.get("som", "N/A"))
    c4.metric("Growth Rate", m.get("growth_rate", "N/A"))
    st.write(m.get("summary", ""))

    left, right = st.columns(2)
    with left:
        st.subheader("Market Trends")
        trends = m.get("trends", [])
        if trends:
            df = pd.DataFrame(trends).set_index("year")
            st.line_chart(df)
        st.markdown("**Opportunities**")
        for o in m.get("opportunities", []):
            st.write(f"- {o}")
        st.markdown("**Challenges**")
        for c in m.get("challenges", []):
            st.write(f"- {c}")
    with right:
        st.subheader("Competitor Landscape")
        comps = p.get("competitors", [])
        if comps:
            st.dataframe(pd.DataFrame(comps), hide_index=True, use_container_width=True)


def show_strategic_dashboard(p: dict):
    pid = p["project_id"]

    sub_t1, sub_t2, sub_t3 = st.tabs([
        "⚡ 1. Risk Score Engine",
        "▦ 2. SWOT Analysis",
        "📋 3. Feasibility Assessment"
    ])

    # ----------------------------------------------------
    # TAB 1: Risk Score Engine
    # ----------------------------------------------------
    with sub_t1:
        st.subheader("Risk Score Engine")
        st.caption("Mathematical rule-based prediction using 5 weighted risk factors")

        r = p.get("risk_assessment")
        col_view, col_tune = st.columns([1.2, 1])

        with col_view:
            if not r:
                st.warning("No risk score generated yet for this project.")
                if st.button("⚡ Calculate Risk Score", key=f"btn_calc_risk_{pid}"):
                    with st.spinner("Calculating risk score using risk engine..."):
                        res = requests.post(f"{API}/api/projects/{pid}/risk-assessment", timeout=30)
                        if res.ok:
                            st.success("Risk Score calculated!")
                            st.rerun()
                        else:
                            st.error(res.text)
            else:
                score = r.get("overall_risk_score", 0.0)
                level = r.get("risk_level", "Medium")
                prob = r.get("success_probability_indicator", 100 - score)

                # Cutoffs: <35 Low (Green), <65 Medium (Orange), >=65 High (Red)
                if score < 35:
                    color = "#4caf50"
                elif score < 65:
                    color = "#ff9800"
                else:
                    color = "#f44336"

                st.markdown(f"""
                <div class="metric-card">
                    <div style="text-align: center; color: rgba(255,255,255,0.7); font-size: 13px;">OVERALL RISK SCORE</div>
                    <div class="risk-score-display" style="color: {color};">{score}</div>
                    <div class="risk-badge" style="color: {color};">{level} RISK</div>
                    <hr style="border-color: rgba(255,255,255,0.1); margin: 12px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>Success Probability Indicator:</span>
                        <strong style="color: #4caf50;">{prob}%</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(float(prob) / 100)

                st.markdown("##### 📊 Sub-Risk Factors Breakdown (Weights)")
                sub_risks = [
                    ("Market Risk (25%)", r.get("market_risk", 0.0)),
                    ("Financial Risk (20%)", r.get("financial_risk", 0.0)),
                    ("Technical Risk (20%)", r.get("technical_risk", 0.0)),
                    ("Operational Risk (20%)", r.get("operational_risk", 0.0)),
                    ("Competition & Regulatory (15%)", r.get("competition_regulatory_risk", 0.0)),
                ]
                for name, val in sub_risks:
                    st.write(f"**{name}**: `{val}%`")
                    st.progress(min(1.0, float(val) / 100))

        with col_tune:
            st.markdown("##### 🎛️ Interactive Parameter Tuner (1-5 Scale)")
            st.caption("Adjust project parameters to recalculate risk scores in real time:")

            input_data = r.get("input_data", {}) if r else {}
            with st.form(f"tune_risk_form_{pid}"):
                b_adeq = st.slider("Budget Adequacy", 1, 5, int(input_data.get("budget_adequacy", 3)), help="1 (Poor) to 5 (Sufficient)")
                m_val = st.slider("Market Validation", 1, 5, int(input_data.get("market_validation", 3)), help="1 (None) to 5 (Strongly Validated)")
                t_read = st.slider("Technical Readiness", 1, 5, int(input_data.get("technical_readiness", 3)), help="1 (Idea Only) to 5 (Production Ready)")
                t_exp = st.slider("Team Experience", 1, 5, int(input_data.get("team_experience", 3)), help="1 (Novice) to 5 (Seasoned Experts)")
                r_avail = st.slider("Resource Availability", 1, 5, int(input_data.get("resource_availability", 3)), help="1 (Scarce) to 5 (Abundant)")
                c_int = st.slider("Competition Intensity", 1, 5, int(input_data.get("competition_intensity", 3)), help="1 (Low) to 5 (Fierce)")
                reg_comp = st.slider("Regulatory Complexity", 1, 5, int(input_data.get("regulatory_complexity", 2)), help="1 (Simple) to 5 (Heavy)")

                recalc_submit = st.form_submit_button("🔄 Recalculate Risk Engine")

            if recalc_submit:
                custom_input = {
                    "budget_adequacy": b_adeq,
                    "market_validation": m_val,
                    "technical_readiness": t_read,
                    "team_experience": t_exp,
                    "resource_availability": r_avail,
                    "competition_intensity": c_int,
                    "regulatory_complexity": reg_comp
                }
                res = requests.post(f"{API}/api/projects/{pid}/risk-assessment", json=custom_input, timeout=30)
                if res.ok:
                    st.success("Risk Score recalculated with new ratings!")
                    st.rerun()
                else:
                    st.error(res.text)

    # ----------------------------------------------------
    # TAB 2: SWOT Analysis
    # ----------------------------------------------------
    with sub_t2:
        st.subheader("SWOT Analysis")
        st.caption("AI strategic evaluation based on project idea and competitive landscape")

        swot = p.get("swot_analysis")
        if not swot:
            st.warning("No SWOT analysis generated yet for this project.")
            if st.button("▦ Generate SWOT with AI", key=f"btn_gen_swot_{pid}"):
                with st.spinner("Generating SWOT analysis with AI..."):
                    res = requests.post(f"{API}/api/projects/{pid}/swot", timeout=120)
                    if res.ok:
                        st.success("SWOT Analysis generated!")
                        st.rerun()
                    else:
                        st.error(res.text)
        else:
            if swot.get("summary"):
                st.info(f"**Executive Summary:** {swot['summary']}")

            strengths = swot.get("strengths", [])
            weaknesses = swot.get("weaknesses", [])
            opportunities = swot.get("opportunities", [])
            threats = swot.get("threats", [])

            s_col, w_col = st.columns(2)
            with s_col:
                items_html = "".join([f"<li style='margin-bottom: 4px;'>{s}</li>" for s in strengths])
                st.markdown(f"""
                <div class="swot-card swot-strengths">
                    <div class="swot-title" style="color: #81c784;">🟢 Strengths</div>
                    <ul style="font-size: 13px; padding-left: 18px; margin: 0; color: rgba(255,255,255,0.9);">{items_html}</ul>
                </div>
                """, unsafe_allow_html=True)

            with w_col:
                items_html = "".join([f"<li style='margin-bottom: 4px;'>{w}</li>" for w in weaknesses])
                st.markdown(f"""
                <div class="swot-card swot-weaknesses">
                    <div class="swot-title" style="color: #e57373;">🔴 Weaknesses</div>
                    <ul style="font-size: 13px; padding-left: 18px; margin: 0; color: rgba(255,255,255,0.9);">{items_html}</ul>
                </div>
                """, unsafe_allow_html=True)

            o_col, t_col = st.columns(2)
            with o_col:
                items_html = "".join([f"<li style='margin-bottom: 4px;'>{o}</li>" for o in opportunities])
                st.markdown(f"""
                <div class="swot-card swot-opportunities">
                    <div class="swot-title" style="color: #64b5f6;">📈 Opportunities</div>
                    <ul style="font-size: 13px; padding-left: 18px; margin: 0; color: rgba(255,255,255,0.9);">{items_html}</ul>
                </div>
                """, unsafe_allow_html=True)

            with t_col:
                items_html = "".join([f"<li style='margin-bottom: 4px;'>{t}</li>" for t in threats])
                st.markdown(f"""
                <div class="swot-card swot-threats">
                    <div class="swot-title" style="color: #ffb74d;">⚠️ Threats</div>
                    <ul style="font-size: 13px; padding-left: 18px; margin: 0; color: rgba(255,255,255,0.9);">{items_html}</ul>
                </div>
                """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 3: Feasibility Assessment
    # ----------------------------------------------------
    with sub_t3:
        st.subheader("Feasibility Assessment")
        st.caption("Resources, Timeline, Advantages, and Proof of Concept")

        feas = p.get("feasibility_assessment")
        if not feas:
            st.warning("No feasibility assessment generated yet for this project.")
            if st.button("📋 Run Feasibility Assessment", key=f"btn_gen_feas_{pid}"):
                with st.spinner("Assessing project feasibility with AI..."):
                    res = requests.post(f"{API}/api/projects/{pid}/feasibility", timeout=120)
                    if res.ok:
                        st.success("Feasibility Assessment completed!")
                        st.rerun()
                    else:
                        st.error(res.text)
        else:
            f_score = feas.get("feasibility_score", 0.0)
            f_status = feas.get("feasibility_status", "Reviewed")

            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 13px; color: rgba(255,255,255,0.7);">FEASIBILITY SCORE</div>
                <div style="font-size: 50px; font-weight: 800; color: #26a69a; margin: 6px 0;">{f_score}%</div>
                <div style="font-size: 14px; font-style: italic; color: rgba(255,255,255,0.85);">{f_status}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 📌 Detailed Feasibility Breakdown")
            st.markdown(f"""
            <div class="feasibility-box">
                <strong>🛠️ Resources & Requirements:</strong>
                <p style="margin: 4px 0 0 0; font-size: 13.5px; color: rgba(255,255,255,0.85);">{feas.get('resources', '')}</p>
            </div>
            <div class="feasibility-box">
                <strong>⏳ Realistic Timeline:</strong>
                <p style="margin: 4px 0 0 0; font-size: 13.5px; color: rgba(255,255,255,0.85);">{feas.get('timeline', '')}</p>
            </div>
            <div class="feasibility-box">
                <strong>🚀 Core Advantages:</strong>
                <p style="margin: 4px 0 0 0; font-size: 13.5px; color: rgba(255,255,255,0.85);">{feas.get('advantages', '')}</p>
            </div>
            <div class="feasibility-box">
                <strong>🔍 Proofs & Market Validation:</strong>
                <p style="margin: 4px 0 0 0; font-size: 13.5px; color: rgba(255,255,255,0.85);">{feas.get('proofs', '')}</p>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# TAB 1: Project Input Form
# ==============================================================================
with tab_input:
    with st.form("project_form"):
        name = st.text_input("Startup / Project Name", placeholder="e.g. FoodFlow Delivery")
        c1, c2 = st.columns(2)
        ptype = c1.selectbox("Project Type", ["startup", "college_project", "hackathon", "business_plan"])
        industry = c2.selectbox("Industry", ["Technology", "Healthcare", "Education", "Finance", "E-commerce", "Food & Beverage", "Logistics", "Other"])
        model = c1.selectbox("Business Model", ["SaaS", "Marketplace", "B2C", "B2B", "Direct-to-Consumer", "Non-profit", "Other"])
        budget = c2.number_input("Budget (USD)", min_value=1.0, value=100000.0, step=1000.0)
        market = st.text_input("Target Market", placeholder="e.g. Metro cities in India")
        desc = st.text_area("Project Description", placeholder="Describe your product idea, target users, and unique selling proposition (min 20 characters)")
        submitted = st.form_submit_button("🚀 Submit & Analyze Project")

    if submitted:
        payload = dict(
            project_name=name,
            project_type=ptype,
            industry=industry,
            business_model=model,
            budget=budget,
            target_market=market,
            description=desc
        )
        try:
            r = requests.post(f"{API}/api/projects", json=payload, timeout=30)
            if r.status_code != 201:
                err_msg = r.text
                try:
                    err_msg = r.json().get("detail", r.text)
                except Exception:
                    pass
                st.error(f"Failed to create project: {err_msg}")
            else:
                p_data = r.json()
                pid = p_data["project_id"]
                st.success(f"Project #{pid} ('{name}') saved successfully!")

                # Step 1: Market Intelligence & Competitors (FIRST)
                with st.spinner("1/4: Analysing market trends & competitors with AI..."):
                    m_resp = requests.post(f"{API}/api/projects/{pid}/analyze", timeout=120)

                # Step 2: Risk Score Engine (SECOND)
                with st.spinner("2/4: Computing Risk Score Engine..."):
                    r_resp = requests.post(f"{API}/api/projects/{pid}/risk-assessment", timeout=30)

                # Step 3: SWOT Analysis
                with st.spinner("3/4: Generating AI SWOT Analysis..."):
                    s_resp = requests.post(f"{API}/api/projects/{pid}/swot", timeout=120)

                # Step 4: Feasibility Assessment
                with st.spinner("4/4: Performing Feasibility Assessment..."):
                    f_resp = requests.post(f"{API}/api/projects/{pid}/feasibility", timeout=120)

                # Fetch updated full project
                full_resp = requests.get(f"{API}/api/projects/{pid}", timeout=10)
                if full_resp.ok:
                    p_data = full_resp.json()

                st.success("🎉 Project Analysis Completed! Review results below:")

                # 1st: Market Analysis & Competitor Landscape (FIRST)
                st.markdown("---")
                st.subheader("📈 Market Intelligence & Competitor Landscape")
                show_market_analysis(p_data)

                # 2nd: Risk Score, SWOT & Feasibility (NEXT)
                st.markdown("---")
                st.subheader("🎯 Risk Assessment, SWOT & Feasibility Evaluation")
                show_strategic_dashboard(p_data)

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend API at http://127.0.0.1:8000. Please ensure the backend server is running.")
        except Exception as e:
            st.error(f"Error: {e}")


# ==============================================================================
# TAB 2: Strategic Evaluation Tab
# ==============================================================================
with tab_strategic:
    try:
        r = requests.get(f"{API}/api/projects", timeout=10)
        if r.status_code == 200:
            all_projects = r.json()
            if not all_projects:
                st.info("No projects recorded yet. Submit a project in 'Project Input' first.")
            else:
                project_names = {f"#{p['project_id']} - {p['project_name']} ({p['project_type']})": p for p in all_projects}
                selected_label = st.selectbox("Select Project to View Strategic Evaluation", list(project_names.keys()))
                selected_proj = project_names[selected_label]

                st.markdown(f"**Industry:** {selected_proj['industry']} | **Model:** {selected_proj['business_model']} | **Budget:** ${selected_proj['budget']:,.2f} | **Target:** {selected_proj['target_market']}")
                st.markdown(f"*{selected_proj['description']}*")
                st.markdown("---")

                # Show Market first, then Strategic Evaluation
                t_mkt, t_strat = st.tabs(["📈 Market & Competitors", "🎯 Risk, SWOT & Feasibility"])
                with t_mkt:
                    show_market_analysis(selected_proj)
                with t_strat:
                    show_strategic_dashboard(selected_proj)
        else:
            st.error("Failed to fetch projects.")
    except Exception as e:
        st.warning(f"Could not connect to backend at {API}. Ensure FastAPI is running.")


# ==============================================================================
# TAB 3: Past Projects
# ==============================================================================
with tab_history:
    try:
        r = requests.get(f"{API}/api/projects", timeout=10)
        if r.status_code == 200:
            projects = r.json()
            if not projects:
                st.info("No projects recorded yet.")
            else:
                for p in projects:
                    with st.expander(f"#{p['project_id']} - {p['project_name']} ({p['project_type']}) - {p['industry']}"):
                        st.markdown(f"**Budget:** ${p['budget']:,.2f} | **Target:** {p['target_market']} | **Created:** {p['created_at']}")
                        st.markdown(f"**Description:** {p['description']}")

                        # 1st Market Analysis, 2nd Risk/SWOT/Feasibility
                        t1, t2 = st.tabs(["📈 Market Intelligence & Competitors", "🎯 Risk, SWOT & Feasibility"])
                        with t1:
                            show_market_analysis(p)
                        with t2:
                            show_strategic_dashboard(p)
    except Exception as e:
        st.warning(f"Could not connect to backend at {API}.")
