from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DoctorModel(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    crm = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    def to_dict(self) -> Optional[Dict[str, Any]]:
        return _model_to_dict(self)


class PatientModel(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    date_of_birth = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    def to_dict(self) -> Optional[Dict[str, Any]]:
        return _model_to_dict(self)


class TriageModel(Base):
    __tablename__ = "triages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    date = Column(String, nullable=True)
    path = Column(String, nullable=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    main_doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    patient = relationship("PatientModel")
    main_doctor = relationship("DoctorModel")
    
    def to_dict(self) -> Optional[Dict[str, Any]]:
        return _model_to_dict(self)


def _to_serializable(val):
    if isinstance(val, datetime):
        return val.isoformat()
    return val


def _model_to_dict(model) -> Optional[Dict[str, Any]]:
    if model is None:
        return None
    result = {}
    for col in model.__table__.columns:
        result[col.name] = _to_serializable(getattr(model, col.name))
    return result
