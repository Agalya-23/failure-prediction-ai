from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from . import models, schemas
from .database import Base, engine, get_db
from .llm import analyse_market, generate_swot, generate_feasibility, estimate_risk_inputs
from .services.risk_engine import calculate_risk

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Failure Prediction AI")

TAG_M2 = "Risk, SWOT & Feasibility"


# --- Default Endpoints ---
@app.get("/", tags=["default"])
def root():
    return {"message": "Failure Prediction AI Backend is running"}


@app.get("/health", tags=["default"])
def health():
    return {"status": "ok"}


# --- Project Core Endpoints ---
@app.post("/api/projects", response_model=schemas.ProjectOut, status_code=201, tags=["Projects"])
@app.post("/projects", response_model=schemas.ProjectOut, status_code=201, include_in_schema=False)
def create_project(data: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/api/projects", response_model=list[schemas.ProjectOut], tags=["Projects"])
@app.get("/projects", response_model=list[schemas.ProjectOut], include_in_schema=False)
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(
        models.Project.created_at.desc()
    ).all()


@app.get("/api/projects/{project_id}", response_model=schemas.ProjectOut, tags=["Projects"])
@app.get("/projects/{project_id}", response_model=schemas.ProjectOut, include_in_schema=False)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


# --- Milestone 1: Market Intelligence ---
@app.post("/api/projects/{project_id}/analyze", response_model=schemas.ProjectOut, tags=["Projects"])
@app.post("/projects/{project_id}/analyze", response_model=schemas.ProjectOut, include_in_schema=False)
def analyze_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    try:
        result = analyse_market(project)
    except Exception as e:
        raise HTTPException(502, f"AI analysis failed: {e}")

    project.market_analysis = models.MarketAnalysis(**result["market"])
    project.competitors = [
        models.CompetitorAnalysis(**c)
        for c in result["competitors"]
    ]

    db.commit()
    db.refresh(project)
    return project


# ==============================================================================
# MILESTONE 2: Risk, SWOT & Feasibility Endpoints
# ==============================================================================

# 1. Risk Assessment Endpoints
@app.post(
    "/api/projects/{project_id}/risk-assessment",
    response_model=schemas.RiskAssessmentOut,
    summary="Create Risk Assessment",
    tags=[TAG_M2]
)
@app.post("/projects/{project_id}/risk-assessment", response_model=schemas.RiskAssessmentOut, include_in_schema=False)
def create_risk_assessment(
    project_id: int,
    risk_input: schemas.RiskInput | None = Body(default=None),
    db: Session = Depends(get_db)
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    if risk_input is None:
        estimated_data = estimate_risk_inputs(project)
        risk_input = schemas.RiskInput(**estimated_data)

    calc = calculate_risk(risk_input)

    risk_obj = models.RiskAssessment(
        project_id=project.project_id,
        financial_risk=calc["financial_risk"],
        market_risk=calc["market_risk"],
        technical_risk=calc["technical_risk"],
        operational_risk=calc["operational_risk"],
        competition_regulatory_risk=calc["competition_regulatory_risk"],
        overall_risk_score=calc["overall_risk_score"],
        risk_level=calc["risk_level"],
        success_probability_indicator=calc["success_probability_indicator"],
        input_data=calc["input_data"],
    )

    project.risk_assessment = risk_obj
    db.commit()
    db.refresh(project)
    return project.risk_assessment


@app.get(
    "/api/projects/{project_id}/risk-assessment",
    response_model=schemas.RiskAssessmentOut,
    summary="Get Latest Risk Assessment",
    tags=[TAG_M2]
)
@app.get("/projects/{project_id}/risk-assessment", response_model=schemas.RiskAssessmentOut, include_in_schema=False)
def get_risk_assessment(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if not project.risk_assessment:
        raise HTTPException(404, "Risk assessment not yet created for this project")
    return project.risk_assessment


# 2. SWOT Endpoints
@app.post(
    "/api/projects/{project_id}/swot",
    response_model=schemas.SWOTOut,
    summary="Create Swot",
    tags=[TAG_M2]
)
@app.post("/projects/{project_id}/swot", response_model=schemas.SWOTOut, include_in_schema=False)
def create_swot(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    try:
        result = generate_swot(project)
    except Exception as e:
        raise HTTPException(502, f"AI SWOT generation failed: {e}")

    swot_obj = models.SWOTAnalysis(
        project_id=project.project_id,
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        opportunities=result["opportunities"],
        threats=result["threats"],
        summary=result.get("summary"),
    )

    project.swot_analysis = swot_obj
    db.commit()
    db.refresh(project)
    return project.swot_analysis


@app.get(
    "/api/projects/{project_id}/swot",
    response_model=schemas.SWOTOut,
    summary="Get Latest Swot",
    tags=[TAG_M2]
)
@app.get("/projects/{project_id}/swot", response_model=schemas.SWOTOut, include_in_schema=False)
def get_swot(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if not project.swot_analysis:
        raise HTTPException(404, "SWOT analysis not yet created for this project")
    return project.swot_analysis


# 3. Feasibility Endpoints
@app.post(
    "/api/projects/{project_id}/feasibility",
    response_model=schemas.FeasibilityOut,
    summary="Create Feasibility",
    tags=[TAG_M2]
)
@app.post("/projects/{project_id}/feasibility", response_model=schemas.FeasibilityOut, include_in_schema=False)
def create_feasibility(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    try:
        result = generate_feasibility(project)
    except Exception as e:
        raise HTTPException(502, f"AI Feasibility assessment failed: {e}")

    feas_obj = models.FeasibilityAssessment(
        project_id=project.project_id,
        resources=result["resources"],
        timeline=result["timeline"],
        advantages=result["advantages"],
        proofs=result["proofs"],
        feasibility_score=result["feasibility_score"],
        feasibility_status=result["feasibility_status"],
    )

    project.feasibility_assessment = feas_obj
    db.commit()
    db.refresh(project)
    return project.feasibility_assessment


@app.get(
    "/api/projects/{project_id}/feasibility",
    response_model=schemas.FeasibilityOut,
    summary="Get Latest Feasibility",
    tags=[TAG_M2]
)
@app.get("/projects/{project_id}/feasibility", response_model=schemas.FeasibilityOut, include_in_schema=False)
def get_feasibility(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if not project.feasibility_assessment:
        raise HTTPException(404, "Feasibility assessment not yet created for this project")
    return project.feasibility_assessment

