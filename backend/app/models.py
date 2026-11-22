
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
