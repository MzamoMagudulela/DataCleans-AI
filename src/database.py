"""
Database Module
Manages SQLite metadata storage and audit trails using SQLAlchemy ORM.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from config.settings import DATABASE_URL

Base = declarative_base()


def utc_now() -> datetime:
    """Helper to return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class DatasetAudit(Base):
    """Stores high-level metadata for each dataset uploaded and analyzed."""
    __tablename__ = "dataset_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    initial_rows = Column(Integer, nullable=False)
    initial_columns = Column(Integer, nullable=False)
    final_rows = Column(Integer, nullable=True)
    final_columns = Column(Integer, nullable=True)
    health_score = Column(Float, nullable=True)
    final_health_score = Column(Float, nullable=True)
    status = Column(String(50), default="Uploaded")

    steps = relationship("CleaningStep", back_populates="audit", cascade="all, delete-orphan", order_by="CleaningStep.step_number")


class CleaningStep(Base):
    """Stores individual transformation operations applied during a session."""
    __tablename__ = "cleaning_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("dataset_audits.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    operation_name = Column(String(100), nullable=False)
    parameters_json = Column(Text, nullable=True)
    affected_rows = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    audit = relationship("DatasetAudit", back_populates="steps")


class DatabaseManager:
    """Provides database initialization and session management."""

    def __init__(self, db_url: str = DATABASE_URL):
        # connect_args={"check_same_thread": False} allows SQLite usage across Streamlit worker threads
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        self.SessionFactory = sessionmaker(bind=self.engine)

    def init_db(self) -> None:
        """Creates tables if they do not exist."""
        Base.metadata.create_all(self.engine)

    def log_dataset_upload(
        self,
        dataset_name: str,
        initial_rows: int,
        initial_columns: int,
        health_score: Optional[float] = None,
    ) -> int:
        """
        Records a new dataset upload event.

        Returns:
            int: The created audit record ID.
        """
        with self.SessionFactory() as session:
            record = DatasetAudit(
                dataset_name=dataset_name,
                initial_rows=initial_rows,
                initial_columns=initial_columns,
                final_rows=initial_rows,
                final_columns=initial_columns,
                health_score=health_score,
                final_health_score=health_score,
                status="Analyzed",
            )
            session.add(record)
            session.commit()
            return record.id

    def log_cleaning_step(
        self,
        audit_id: int,
        step_number: int,
        operation_name: str,
        parameters_json: Optional[str] = None,
        affected_rows: int = 0,
    ) -> int:
        """Records an applied cleaning transformation step."""
        with self.SessionFactory() as session:
            step = CleaningStep(
                audit_id=audit_id,
                step_number=step_number,
                operation_name=operation_name,
                parameters_json=parameters_json,
                affected_rows=affected_rows,
            )
            session.add(step)
            session.commit()
            return step.id

    def update_audit_completion(
        self,
        audit_id: int,
        final_rows: int,
        final_columns: int,
        final_health_score: float,
        status: str = "Cleaned",
    ) -> None:
        """Updates the session record with post-cleaning metrics."""
        with self.SessionFactory() as session:
            audit = session.query(DatasetAudit).filter_by(id=audit_id).first()
            if audit:
                audit.final_rows = final_rows
                audit.final_columns = final_columns
                audit.final_health_score = final_health_score
                audit.status = status
                session.commit()

    def get_recent_audits(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Retrieves recent audit sessions."""
        with self.SessionFactory() as session:
            audits = (
                session.query(DatasetAudit)
                .order_by(DatasetAudit.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": a.id,
                    "dataset_name": a.dataset_name,
                    "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else "",
                    "initial_rows": a.initial_rows,
                    "initial_columns": a.initial_columns,
                    "final_rows": a.final_rows,
                    "final_columns": a.final_columns,
                    "initial_health_score": a.health_score,
                    "final_health_score": a.final_health_score,
                    "status": a.status,
                    "total_steps": len(a.steps),
                }
                for a in audits
            ]

    def get_audit_steps(self, audit_id: int) -> List[Dict[str, Any]]:
        """Retrieves all cleaning steps associated with a specific audit session."""
        with self.SessionFactory() as session:
            steps = (
                session.query(CleaningStep)
                .filter_by(audit_id=audit_id)
                .order_by(CleaningStep.step_number.asc())
                .all()
            )
            return [
                {
                    "step_number": s.step_number,
                    "operation_name": s.operation_name,
                    "parameters_json": s.parameters_json,
                    "affected_rows": s.affected_rows,
                    "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "",
                }
                for s in steps
            ]
