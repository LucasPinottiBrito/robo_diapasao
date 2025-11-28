from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from .config import get_session
from .models import DoctorModel
from sqlalchemy import select

class DoctorRepository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
        self._close = session is None

    def create(self, name: str, cpf: str, crm: Optional[str] = None) -> int:
        doc = DoctorModel(name=name, cpf=cpf, crm=crm)
        self.session.add(doc)
        self.session.commit()
        self.session.refresh(doc)
        return doc.id

    def get(self, doctor_id: int) -> Optional[Dict[str, Any]]:
        return DoctorModel.to_dict(self.session.get(DoctorModel, doctor_id))

    def list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        stmt = select(DoctorModel).order_by(DoctorModel.id).limit(limit).offset(offset)
        results = self.session.execute(stmt).scalars().all()
        return [r.to_dict() for r in results]

    def update(self, doctor_id: int, updates: Dict[str, Any]) -> bool:
        doc = self.session.get(DoctorModel, doctor_id)
        if not doc:
            return False
        for k, v in updates.items():
            setattr(doc, k, v)
        self.session.commit()
        return True

    def delete(self, doctor_id: int) -> bool:
        doc = self.session.get(DoctorModel, doctor_id)
        if not doc:
            return False
        self.session.delete(doc)
        self.session.commit()
        return True

    def __del__(self):
        if self._close:
            self.session.close()
