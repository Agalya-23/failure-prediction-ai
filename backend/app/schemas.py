
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

class ProjectOut(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    project_id: int
    created_at: datetime
    market_analysis: MarketOut | None = None
    competitors: list[CompetitorOut] = []
