from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, func, select, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session as _Session
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class DoctorModel(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    crm = Column(String)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)


class PatientModel(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    date_of_birth = Column(String)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)


class TriageModel(Base):
    __tablename__ = "triages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    date = Column(String)
    path = Column(String)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    main_doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)


def _to_serializable(val):
    if isinstance(val, datetime):
        return val.isoformat()
    return val


def _model_to_dict(model) -> Dict[str, Any]:
    if model is None:
        return None
    result = {}
    for col in model.__table__.columns:
        result[col.name] = _to_serializable(getattr(model, col.name))
    return result


class Database:
    def __init__(self, path: str = "database.db"):
        self.path = path
        self.engine = create_engine(
            f"sqlite:///{self.path}",
            connect_args={"check_same_thread": False},
            echo=False,
            future=True,
        )
        # Ensure SQLite enforces foreign keys
        @event.listens_for(self.engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False, class_=_Session)

    def close(self):
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def init_schema(self):
        Base.metadata.create_all(self.engine)

    # Doctors CRUD
    def create_doctor(self, name: str, cpf: str, crm: Optional[str] = None) -> int:
        with self.Session() as session:
            doctor = DoctorModel(name=name, cpf=cpf, crm=crm)
            session.add(doctor)
            session.commit()
            session.refresh(doctor)
            return doctor.id

    def get_doctor(self, doctor_id: int) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            doc = session.get(DoctorModel, doctor_id)
            return _model_to_dict(doc)

    def list_doctors(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with self.Session() as session:
            stmt = select(DoctorModel).order_by(DoctorModel.id).limit(limit).offset(offset)
            results = session.execute(stmt).scalars().all()
            return [_model_to_dict(r) for r in results]

    def update_doctor(self, doctor_id: int, name: Optional[str] = None,
                      cpf: Optional[str] = None, crm: Optional[str] = None) -> bool:
        with self.Session() as session:
            doc = session.get(DoctorModel, doctor_id)
            if doc is None:
                return False
            changed = False
            if name is not None:
                doc.name = name
                changed = True
            if cpf is not None:
                doc.cpf = cpf
                changed = True
            if crm is not None:
                doc.crm = crm
                changed = True
            if not changed:
                return False
            session.commit()
            return True

    def delete_doctor(self, doctor_id: int) -> bool:
        with self.Session() as session:
            doc = session.get(DoctorModel, doctor_id)
            if doc is None:
                return False
            session.delete(doc)
            session.commit()
            return True

    # Patients CRUD
    def create_patient(self, name: str, cpf: str, date_of_birth: Optional[str] = None) -> int:
        with self.Session() as session:
            patient = PatientModel(name=name, cpf=cpf, date_of_birth=date_of_birth)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            return patient.id

    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            p = session.get(PatientModel, patient_id)
            return _model_to_dict(p)

    def list_patients(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with self.Session() as session:
            stmt = select(PatientModel).order_by(PatientModel.id).limit(limit).offset(offset)
            results = session.execute(stmt).scalars().all()
            return [_model_to_dict(r) for r in results]

    def update_patient(self, patient_id: int, name: Optional[str] = None,
                       cpf: Optional[str] = None, date_of_birth: Optional[str] = None) -> bool:
        with self.Session() as session:
            p = session.get(PatientModel, patient_id)
            if p is None:
                return False
            changed = False
            if name is not None:
                p.name = name
                changed = True
            if cpf is not None:
                p.cpf = cpf
                changed = True
            if date_of_birth is not None:
                p.date_of_birth = date_of_birth
                changed = True
            if not changed:
                return False
            session.commit()
            return True

    def delete_patient(self, patient_id: int) -> bool:
        with self.Session() as session:
            p = session.get(PatientModel, patient_id)
            if p is None:
                return False
            session.delete(p)
            session.commit()
            return True

    # Triages CRUD
    def create_triage(self, code: str, date: Optional[str], path: Optional[str],
                      patient_id: int, main_doctor_id: Optional[int] = None) -> int:
        with self.Session() as session:
            t = TriageModel(code=code, date=date, path=path, patient_id=patient_id, main_doctor_id=main_doctor_id)
            session.add(t)
            session.commit()
            session.refresh(t)
            return t.id

    def get_triage(self, triage_id: int) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            t = session.get(TriageModel, triage_id)
            return _model_to_dict(t)

    def list_triages(self, limit: int = 100, offset: int = 0, patient_id: Optional[int] = None,
                     doctor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.Session() as session:
            stmt = select(TriageModel)
            if patient_id is not None:
                stmt = stmt.where(TriageModel.patient_id == patient_id)
            if doctor_id is not None:
                stmt = stmt.where(TriageModel.main_doctor_id == doctor_id)
            stmt = stmt.order_by(TriageModel.id).limit(limit).offset(offset)
            results = session.execute(stmt).scalars().all()
            return [_model_to_dict(r) for r in results]

    def update_triage(self, triage_id: int, code: Optional[str] = None, date: Optional[str] = None,
                      path: Optional[str] = None, patient_id: Optional[int] = None,
                      main_doctor_id: Optional[int] = None) -> bool:
        with self.Session() as session:
            t = session.get(TriageModel, triage_id)
            if t is None:
                return False
            changed = False
            if code is not None:
                t.code = code
                changed = True
            if date is not None:
                t.date = date
                changed = True
            if path is not None:
                t.path = path
                changed = True
            if patient_id is not None:
                t.patient_id = patient_id
                changed = True
            if main_doctor_id is not None:
                t.main_doctor_id = main_doctor_id
                changed = True
            if not changed:
                return False
            session.commit()
            return True

    def delete_triage(self, triage_id: int) -> bool:
        with self.Session() as session:
            t = session.get(TriageModel, triage_id)
            if t is None:
                return False
            session.delete(t)
            session.commit()
            return True


# Convenience module-level functions using default DB file path
_default_db_path = os.environ.get("ROBO_DB_PATH", "database.db")
_default_db = Database(_default_db_path)


def init_schema(path: Optional[str] = None):
    if path:
        with Database(path) as db:
            db.init_schema()
    else:
        _default_db.init_schema()
