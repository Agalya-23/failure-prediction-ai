
from datetime import datetime
from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[int] = mapped_column(primary_key=True)
    project_name: Mapped[str] = mapped_column(String(200))
    project_type: Mapped[str] = mapped_column(String(50))
    industry: Mapped[str] = mapped_column(String(100))
    business_model: Mapped[str] = mapped_column(String(100))
    budget: Mapped[float] = mapped_column(Numeric(14, 2))
    target_market: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    market_analysis: Mapped["MarketAnalysis | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan")

    competitors: Mapped[list["CompetitorAnalysis"]] = relationship(
        back_populates="project", cascade="all, delete-orphan")

    risk_assessment: Mapped["RiskAssessment | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan")

    swot_analysis: Mapped["SWOTAnalysis | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan")

    feasibility_assessment: Mapped["FeasibilityAssessment | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan")


class MarketAnalysis(Base):
    __tablename__ = "market_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    tam: Mapped[str] = mapped_column(String(50))
    sam: Mapped[str] = mapped_column(String(50))
    som: Mapped[str] = mapped_column(String(50))
    growth_rate: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(Text)
    trends: Mapped[list] = mapped_column(JSON)
    opportunities: Mapped[list] = mapped_column(JSON)
    challenges: Mapped[list] = mapped_column(JSON)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="market_analysis")


class CompetitorAnalysis(Base):
    __tablename__ = "competitor_analysis"

    analysis_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    competitor_name: Mapped[str] = mapped_column(String(200))
    competitor_type: Mapped[str] = mapped_column(String(20))
    market_position: Mapped[str] = mapped_column(Text)
    competitive_risk: Mapped[str] = mapped_column(String(20))
    analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="competitors")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    financial_risk: Mapped[float] = mapped_column(Numeric(5, 2))
    market_risk: Mapped[float] = mapped_column(Numeric(5, 2))
    technical_risk: Mapped[float] = mapped_column(Numeric(5, 2))
    operational_risk: Mapped[float] = mapped_column(Numeric(5, 2))
    competition_regulatory_risk: Mapped[float] = mapped_column(Numeric(5, 2))
    overall_risk_score: Mapped[float] = mapped_column(Numeric(5, 2))
    risk_level: Mapped[str] = mapped_column(String(50))
    success_probability_indicator: Mapped[float] = mapped_column(Numeric(5, 2))
    input_data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="risk_assessment")


class SWOTAnalysis(Base):
    __tablename__ = "swot_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    strengths: Mapped[list] = mapped_column(JSON)
    weaknesses: Mapped[list] = mapped_column(JSON)
    opportunities: Mapped[list] = mapped_column(JSON)
    threats: Mapped[list] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="swot_analysis")


class FeasibilityAssessment(Base):
    __tablename__ = "feasibility_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    resources: Mapped[str] = mapped_column(Text)
    timeline: Mapped[str] = mapped_column(Text)
    advantages: Mapped[str] = mapped_column(Text)
    proofs: Mapped[str] = mapped_column(Text)
    feasibility_score: Mapped[float] = mapped_column(Numeric(5, 2))
    feasibility_status: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="feasibility_assessment")
