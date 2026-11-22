
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import Base, engine, get_db
from .llm import analyse_market

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Failure Prediction AI")


@app.post("/projects", response_model=schemas.ProjectOut, status_code=201)
def create_project(data: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(
        models.Project.created_at.desc()
    ).all()


@app.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)

    if not project:
        raise HTTPException(404, "Project not found")

    return project


@app.post("/projects/{project_id}/analyze", response_model=schemas.ProjectOut)
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
