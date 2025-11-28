from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from .config import get_session
from .models import PatientModel
from sqlalchemy import select

class PatientRepository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
        self._close = session is None

    def create(self, name: str, cpf: str, date_of_birth: Optional[str] = None) -> int:
        p = PatientModel(name=name, cpf=cpf, date_of_birth=date_of_birth)
        self.session.add(p)
        self.session.commit()
        self.session.refresh(p)
        return p.id

    def get(self, patient_id: int) -> Optional[Dict[str, Any]]:
        p = self.session.get(PatientModel, patient_id)
        return p.to_dict() if p else None

    def list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        stmt = select(PatientModel).order_by(PatientModel.id).limit(limit).offset(offset)
        results = self.session.execute(stmt).scalars().all()
        return [r.to_dict() for r in results]

    def update(self, patient_id: int, updates: Dict[str, Any]) -> bool:
        p = self.session.get(PatientModel, patient_id)
        if not p:
            return False
        for k, v in updates.items():
            setattr(p, k, v)
        self.session.commit()
        return True

    def delete(self, patient_id: int) -> bool:
        p = self.session.get(PatientModel, patient_id)
        if not p:
            return False
        self.session.delete(p)
        self.session.commit()
        return True

    def __del__(self):
        if self._close:
            self.session.close()
