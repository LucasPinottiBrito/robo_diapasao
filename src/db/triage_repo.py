from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from .config import get_session
from .models import TriageModel, DoctorModel, PatientModel
from sqlalchemy import select

class TriageRepository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
        self._close = session is None

    def create(self, code: str, date: Optional[str], path: Optional[str],
               patient_id: int, main_doctor_id: Optional[int] = None) -> int:
        t = TriageModel(code=code, date=date, path=path,
                        patient_id=patient_id, main_doctor_id=main_doctor_id)
        self.session.add(t)
        self.session.commit()
        self.session.refresh(t)
        return t.id

    def get(self, triage_id: int) -> Optional[Dict[str, Any]]:
        t = self.session.get(TriageModel, triage_id)
        return t.to_dict() if t else None

    def list(self, limit: int = 100, offset: int = 0,
             patient_id: Optional[int] = None,
             doctor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        stmt = select(TriageModel)
        if patient_id:
            stmt = stmt.where(TriageModel.patient_id == patient_id)
        if doctor_id:
            stmt = stmt.where(TriageModel.main_doctor_id == doctor_id)

        stmt = stmt.order_by(TriageModel.id).limit(limit).offset(offset)
        results = self.session.execute(stmt).scalars().all()
        return [r.to_dict() for r in results]

    def update(self, triage_id: int, updates: Dict[str, Any]) -> bool:
        t = self.session.get(TriageModel, triage_id)
        if not t:
            return False
        for k, v in updates.items():
            setattr(t, k, v)
        self.session.commit()
        return True

    def delete(self, triage_id: int) -> bool:
        t = self.session.get(TriageModel, triage_id)
        if not t:
            return False
        self.session.delete(t)
        self.session.commit()
        return True

    def __del__(self):
        if self._close:
            self.session.close()
