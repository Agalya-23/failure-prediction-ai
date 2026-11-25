
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class ProjectCreate(BaseModel):
    project_name: str = Field(min_length=2, max_length=200)
    project_type: Literal["startup", "college_project", "hackathon", "business_plan"]
    industry: str
    business_model: str
    budget: float = Field(gt=0)
    target_market: str
    description: str = Field(min_length=20)

class CompetitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    competitor_name: str
    competitor_type: str
    market_position: str
    competitive_risk: str

class MarketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tam: str
    sam: str
    som: str
    growth_rate: str
    summary: str
    trends: list
    opportunities: list
    challenges: list

class RiskInput(BaseModel):
    budget_adequacy: int = Field(default=3, ge=1, le=5, description="1 (Poor) to 5 (Excellent)")
    market_validation: int = Field(default=3, ge=1, le=5, description="1 (None) to 5 (Validated)")
    technical_readiness: int = Field(default=3, ge=1, le=5, description="1 (Concept) to 5 (Production)")
    team_experience: int = Field(default=3, ge=1, le=5, description="1 (Novice) to 5 (Expert)")
    resource_availability: int = Field(default=3, ge=1, le=5, description="1 (Scarce) to 5 (Abundant)")
    competition_intensity: int = Field(default=3, ge=1, le=5, description="1 (Low) to 5 (Fierce)")
    regulatory_complexity: int = Field(default=3, ge=1, le=5, description="1 (Simple) to 5 (Heavy)")

class RiskAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    project_id: int | None = None
    financial_risk: float
    market_risk: float
    technical_risk: float
    operational_risk: float
    competition_regulatory_risk: float
    overall_risk_score: float
    risk_level: str
    success_probability_indicator: float
    input_data: dict
    created_at: datetime | None = None

class SWOTOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    project_id: int | None = None
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]
    summary: str | None = None
    created_at: datetime | None = None

class FeasibilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    project_id: int | None = None
    resources: str
    timeline: str
    advantages: str
    proofs: str
    feasibility_score: float
    feasibility_status: str
    created_at: datetime | None = None

class ProjectOut(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    project_id: int
    created_at: datetime
    market_analysis: MarketOut | None = None
    competitors: list[CompetitorOut] = []
    risk_assessment: RiskAssessmentOut | None = None
    swot_analysis: SWOTOut | None = None
    feasibility_assessment: FeasibilityOut | None = None
